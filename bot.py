import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)
from datetime import datetime, timedelta
from pylatex import Document, LongTable, NoEscape
import holidays

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
)

# Conversation states
CORPUS, FLOOR, NUM_ROOMS, USER_ROOM, USER_NAME, DAYS_AHEAD, CONFIRMATION = range(7)

def generate_pdf(corpus, floor, num_rooms, your_room_number, username, start_date, num_days):
    """
    Generate the schedule PDF based on the user's input and return the file path.
    """
    os.makedirs("Schedule", exist_ok=True)
    output_filename = f"Schedule/schedule_for_{corpus.lower()}_{floor}"
    logging.info(f"Generating PDF file: {output_filename}")

    # getting holidays using the holidays library
    # dk_holidays = holidays.CountryHoliday('DK', years=[2024, 2025])

    # parsing the start date
    start_date = datetime.strptime(start_date, '%d.%m.%Y')

    # preparing the document with uniform margins and updated font size
    doc = Document()
    doc.preamble.append(NoEscape(r'\usepackage[table,xcdraw]{xcolor}'))
    doc.preamble.append(NoEscape(r'\usepackage{longtable}'))
    doc.preamble.append(NoEscape(r'\usepackage[left=1cm,right=2.2cm,top=1cm,bottom=1cm]{geometry}'))
    doc.preamble.append(NoEscape(r'\usepackage{setspace}'))
    doc.preamble.append(NoEscape(r'\setlength{\parindent}{0pt}'))
    doc.preamble.append(NoEscape(r'\renewcommand{\familydefault}{\sfdefault}'))
    doc.preamble.append(NoEscape(r'\pagenumbering{gobble}'))  # remove page numbering

    # setting font size for the entire document
    doc.append(NoEscape(r'\fontsize{14pt}{16pt}\selectfont'))

    # centering the table itself
    doc.append(NoEscape(r'\begin{center}'))
    doc.append(NoEscape(r'Kitchen Cleaning Schedule'))

    # creating a longtable for multi-page support
    with doc.create(LongTable(r'|p{0.3\textwidth}|p{0.55\textwidth}|p{0.15\textwidth}|')) as table:
        table.add_hline()
        table.add_row(["Room Number", "Date (Day of the Week, dd.mm.yy)", "Checkin"])
        table.add_hline()
        table.end_table_header()
        table.add_hline()

        # adding table rows
        room_number_index = 1
        for i in range(num_days):
            # calculating the current date
            current_date = start_date + timedelta(days=i)

            # # check if the current date is a holiday
            # if current_date in dk_holidays:
            #     holiday_name = dk_holidays.get(current_date)
            #     # add a row for holidays with the holiday name
            #     holidate = NoEscape(f"{current_date.strftime('%A')} \\hfill {current_date.strftime('%d.%m.%Y')}")
            #     table.add_row([holiday_name, holidate, ""])
            #     table.add_hline()
            #     continue

            # calculating the room number
            room_number = (
                f"{corpus}.{floor}.{room_number_index}"
                if room_number_index < 10
                else f"{corpus}.{floor}.{room_number_index}"
            )

            # checking if the current room is the user's room
            resident = username if room_number_index == your_room_number else ""

            # formatting the date with \hfill
            day_of_week = current_date.strftime('%A')
            date = current_date.strftime('%d.%m.%Y')
            formatted_date = NoEscape(f"{day_of_week}\\hfill {date}")

            # adding a row to the table
            table.add_row([room_number, formatted_date, ""])
            table.add_hline()

            # increment room number index
            room_number_index = (room_number_index % num_rooms) + 1

    doc.append(NoEscape(r'\end{center}'))
    doc.generate_pdf(output_filename, clean_tex=False)
    return output_filename

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        ["1A", "1B", "1C", "1D"],
        ["2A", "2B", "2C", "2D"],
        ["3A", "3B", "3C", "3D"],
        ["4A", "4B", "4C", "4D"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome to the Dorm Management Bot! Let's set up your room schedule.\n\n"
        "Please select the corpus:",
        reply_markup=reply_markup
    )
    return CORPUS

async def get_corpus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["corpus"] = update.message.text
    keyboard = [
        ["0"],
        ["1"],
        ["2"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Great! Now, enter the floor number:", reply_markup=reply_markup)
    return FLOOR

async def get_floor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["floor"] = update.message.text
    await update.message.reply_text("How many rooms are on this floor?")
    return NUM_ROOMS

async def get_num_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["num_rooms"] = int(update.message.text)
    num_rooms = context.user_data["num_rooms"]
    keyboard = []
    for i in range(1, num_rooms + 1, 3):
        row = [InlineKeyboardButton(str(j), callback_data=str(j)) for j in range(i, min(i + 3, num_rooms + 1))]
        keyboard.append(row)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Which room number is yours?", reply_markup=reply_markup)
    return USER_ROOM

async def get_user_room(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["your_room_number"] = int(query.data)
    await query.edit_message_text(text=f"You selected room number: {query.data}")
    await query.message.reply_text("What is your name?")
    return USER_NAME

async def get_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["username"] = update.message.text
    await update.message.reply_text("How many days ahead would you like to generate the schedule for?")
    return DAYS_AHEAD

async def get_days_ahead(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["num_days"] = int(update.message.text)
    user_data = context.user_data
    await update.message.reply_text(
        f"Thank you! Here is the information you provided:\n"
        f"- Corpus: {user_data['corpus']}\n"
        f"- Floor: {user_data['floor']}\n"
        f"- Number of Rooms: {user_data['num_rooms']}\n"
        f"- Your Room: {user_data['your_room_number']}\n"
        f"- Your Name: {user_data['username']}\n"
        f"- Days Ahead: {user_data['num_days']}\n\n"
        "Press the button below to generate your schedule PDF."
    )
    keyboard = [[InlineKeyboardButton("Generate Schedule", callback_data='generate_schedule')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Confirm your schedule generation:", reply_markup=reply_markup)
    return CONFIRMATION

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await generate_schedule(query, context)
    return CONFIRMATION

async def generate_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Generate a PDF schedule based on user data after all info has been collected.
    """
    user_data = context.user_data
    start_date = datetime.now().replace(day=1).strftime('%d.%m.%Y')
    num_days = user_data["num_days"]
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

        keyboard = [[InlineKeyboardButton("Send PDF", callback_data='send_pdf')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Your schedule has been generated! Press the button below to receive the PDF file.", reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"Error generating the PDF: {str(e)}")
        await update.message.reply_text("An error occurred while generating the PDF. Please try again.")

async def send_pdf_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await send_pdf(query, context)
    return CONFIRMATION

async def send_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends the generated PDF file after it's been created.
    """
    user_data = context.user_data
    pdf_file = user_data.get("pdf_file", None)

    if not pdf_file:
        await update.message.reply_text("Error: No schedule PDF has been generated yet. Please press the 'Generate Schedule' button to create it.")
        return
    
    pdf_file = f'{pdf_file}.pdf'

    # Log the file being sent
    logging.info(f"Attempting to send file: {pdf_file}")

    try:
        with open(pdf_file, 'rb') as file:
            await update.message.reply_document(
                file,
                filename=os.path.basename(f'{pdf_file}'),
                caption="Here is your room schedule. Let us know if you need further assistance!"
            )
            logging.info(f"PDF file sent successfully: {pdf_file}")
    except Exception as e:
        logging.error(f"Error while sending the PDF: {str(e)}")
        await update.message.reply_text("An error occurred while sending the PDF.")

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
            USER_ROOM: [CallbackQueryHandler(get_user_room)],
            USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_name)],
            DAYS_AHEAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_days_ahead)],
            CONFIRMATION: [
                CallbackQueryHandler(confirm, pattern='^generate_schedule$'),
                CallbackQueryHandler(send_pdf_callback, pattern='^send_pdf$'),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
