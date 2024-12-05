import os
import logging
import sqlite3
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from datetime import datetime, timedelta
from pylatex import Document, LongTable, NoEscape

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Conversation states
CORPUS, FLOOR, NUM_ROOMS, USER_ROOM, USER_NAME, CONFIRMATION, SAVE = range(7)

# Ensure database exists
db_file = "dorm_data.db"
if not os.path.exists(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            corpus TEXT,
            floor TEXT,
            room_number TEXT,
            resident_name TEXT,
            checkin_status TEXT
        )
    ''')
    conn.commit()
    conn.close()


def generate_pdf(corpus, floor, num_rooms, your_room_number, username, start_date, num_days):
    """
    Generate the schedule PDF based on the user's input and save it to the Schedule directory.
    """
    os.makedirs("Schedule", exist_ok=True)
    output_filename = f"Schedule/schedule_for_{corpus.lower()}.{floor}.pdf"
    logging.info(f"Generating PDF file: {output_filename}")

    start_date = datetime.strptime(start_date, '%d.%m.%Y')
    doc = Document()
    doc.preamble.append(NoEscape(r'\usepackage[table,xcdraw]{xcolor}'))
    doc.preamble.append(NoEscape(r'\usepackage{longtable}'))

    with doc.create(LongTable(r'|p{0.25\textwidth}|p{0.5\textwidth}|p{0.1\textwidth}|p{0.15\textwidth}|')) as table:
        table.add_hline()
        table.add_row(["Room Number", "Date (Day of the Week, dd.mm.yy)", "Checkin", "Residents"])
        table.add_hline()
        table.end_table_header()

        for i in range(num_days):
            room_number_index = (i % num_rooms) + 1
            room_number = f"{corpus}.{floor}.{room_number_index}"
            resident = username if room_number_index == your_room_number else ""
            current_date = start_date + timedelta(days=i)
            day_of_week = current_date.strftime('%A')
            date = current_date.strftime('%d.%m.%Y')
            formatted_date = NoEscape(f"{day_of_week}\\hfill{date}")
            table.add_row([room_number, formatted_date, "", resident])
            table.add_hline()

    doc.generate_pdf(output_filename, clean_tex=False)
    return output_filename


async def save_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends the generated PDF file after it's been created.
    """
    user_data = context.user_data
    pdf_file = user_data.get("pdf_file", None)

    if not pdf_file:
        await update.message.reply_text("Error: No schedule PDF has been generated yet. Please type 'confirm' to generate it.")
        return

    # Log the file being sent
    logging.info(f"Attempting to send file: {pdf_file}")

    try:
        with open(pdf_file, 'rb') as file:
            await update.message.reply_document(
                file,
                filename=os.path.basename(pdf_file),
                caption="Here is your room schedule. Let us know if you need further assistance!"
            )
            logging.info(f"PDF file sent successfully: {pdf_file}")
    except Exception as e:
        logging.error(f"Error while sending the PDF: {str(e)}")
        await update.message.reply_text("An error occurred while sending the PDF.")


async def generate_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Generate a PDF schedule based on user data after all info has been collected.
    """
    user_data = context.user_data
    num_days = 30
    start_date = datetime.now().strftime('%d.%m.%Y')
    corpus = user_data["corpus"]
    floor = user_data["floor"]
    num_rooms = user_data["num_rooms"]
    your_room_number = user_data["your_room_number"]
    username = user_data["username"]

    try:
        # Generate the PDF file using a relative path
        pdf_file = generate_pdf(corpus, floor, num_rooms, your_room_number, username, start_date, num_days)

        # Store the generated PDF file path in user_data for later use
        user_data["pdf_file"] = pdf_file
        logging.info(f"PDF file generated and stored: {pdf_file}")

        await update.message.reply_text(
            "Your schedule has been generated! Type '/save' to receive the PDF file."
        )
    except Exception as e:
        logging.error(f"Error generating the PDF: {str(e)}")
        await update.message.reply_text("An error occurred while generating the PDF. Please try again.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Welcome to the Dorm Management Bot! Let's set up your room schedule.\n\n"
        "Please provide the corpus (e.g., 3D):"
    )
    return CORPUS


async def get_corpus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["corpus"] = update.message.text
    await update.message.reply_text("Great! Now, enter the floor number:")
    return FLOOR


async def get_floor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["floor"] = update.message.text
    await update.message.reply_text("How many rooms are on this floor?")
    return NUM_ROOMS


async def get_num_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["num_rooms"] = int(update.message.text)
    await update.message.reply_text("Which room number is yours?")
    return USER_ROOM


async def get_user_room(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["your_room_number"] = int(update.message.text)
    await update.message.reply_text("What is your name?")
    return USER_NAME


async def get_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["username"] = update.message.text
    await update.message.reply_text(
        f"Thank you! Here is the information you provided:\n"
        f"- Corpus: {context.user_data['corpus']}\n"
        f"- Floor: {context.user_data['floor']}\n"
        f"- Number of Rooms: {context.user_data['num_rooms']}\n"
        f"- Your Room: {context.user_data['your_room_number']}\n"
        f"- Your Name: {context.user_data['username']}\n\n"
        "Type 'confirm' to generate your schedule PDF."
    )
    return CONFIRMATION


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Process canceled. Goodbye!")
    return ConversationHandler.END


def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CORPUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_corpus)],
            FLOOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_floor)],
            NUM_ROOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_num_rooms)],
            USER_ROOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_room)],
            USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_name)],
            CONFIRMATION: [MessageHandler(filters.Regex("^confirm$"), generate_schedule)],
            SAVE: [CommandHandler("save", save_pdf)],  # Add /save command handler
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
