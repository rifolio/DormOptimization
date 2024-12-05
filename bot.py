import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Ensure the Schedule directory and test.txt file exist
os.makedirs("Schedule", exist_ok=True)
test_file_path = "Schedule/schedule_for_3D.2.pdf.pdf"
if not os.path.exists(test_file_path):
    with open(test_file_path, 'w') as f:
        f.write("This is a test file for the Telegram bot.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Responds with "Hello" and sends the test.txt file when the /start command is received.
    """
    try:
        # Send "Hello" message
        await update.message.reply_text("Hello!")
        
        # Send the test.txt file
        with open(test_file_path, 'rb') as file:
            await update.message.reply_document(
                file,
                filename="schedule_for_3D.2.pdf.pdf",
                caption="Here is the test file: schedule_for_3D.2.pdf.pdf"
            )
            logging.info("test.txt sent successfully.")
    except Exception as e:
        logging.error(f"Error sending: {str(e)}")
        await update.message.reply_text("An error occurred while sending the test file.")

def main():
    # Initialize the bot application
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Add the /start command handler
    application.add_handler(CommandHandler("start", start))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
