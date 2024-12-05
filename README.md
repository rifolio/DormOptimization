# Dorm Management Bot

![Python 3.12](https://img.shields.io/badge/Python-3.12-brightgreen.svg) ![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg) ![PyLaTeX](https://img.shields.io/badge/Library-PyLaTeX-orange.svg) ![dotenv](https://img.shields.io/badge/Library-dotenv-green.svg) ![Holidays](https://img.shields.io/badge/Library-Holidays-purple.svg)

> Dorm Management Bot is a Telegram chatbot designed to help dorm residents generate and manage room cleaning schedules. The bot collects relevant details from the user and generates a PDF schedule that is easy to distribute among residents. It uses the `pylatex` library to create uniform and professional-looking PDF documents.

## Features:

- Collects user input through a conversational interface to gather dorm information.
- Automatically calculates the start date as the first day of the current month.
- Lets users define the number of days ahead for generating the schedule.
- Generates and sends a schedule PDF via Telegram.
- Integrates Danish public holidays in the generated schedule [optional].

## Flow of the Bot

1. **Start Command:** _/start_: The bot initiates the setup by asking for the corpus, floor, number of rooms, user's room, name, and the number of days ahead for the schedule.
2. **Generate Schedule**: Once the user has provided all the information, the bot confirms the input and prompts the user with a button to generate the PDF schedule.
3. **Send PDF**: After generating the schedule, the user can press a button to receive the generated PDF through Telegram.

## Installation and Running the Bot

### 1. Clone the Repository

Clone this repository to your local machine using:

```bash
git clone https://github.com/rifolio/DormOptimization
```

---

### 2. Set Up Virtual Environment

Navigate to the project directory and set up a virtual environment by running:

```bash
python3 -m venv venv
```

---

### 3. Activate Virtual Environment

Activate the virtual environment using:

```bash
source venv/bin/activate
```

---

### 4. Install Dependencies

Install the project dependencies using pip:

```bash
pip install -r requirements.txt
```

---

### 5. Set Up Telegram Bot Token in .env File and Run the Project

Create a `.env` file in the root directory and add your Telegram bot token:

```bash
.env:
TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
```

Once the dependencies are installed, you can run the project using:

```bash
python bot.py
```

## License

This project is licensed under the MIT License.
