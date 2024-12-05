from pylatex import Document, LongTable, NoEscape
from datetime import datetime, timedelta
import holidays
import locale

def generate_pdf_table(corpus, floor, number_after_corpus, num_rooms, your_room_number, username, start_date, num_days):
    # Set locale to Ukrainian for correct date formatting
    try:
        locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')
    except locale.Error:
        print("Warning: Ukrainian locale not found. Make sure your system supports 'uk_UA.UTF-8'.")
    
    # Generates a PDF file with a table that contains corresponding dates and residents for room numbers

    # Loading holidays using the holidays library
    # ua_holidays = holidays.CountryHoliday('UA', years=[2024, 2025])

    # Parsing the start date
    start_date = datetime.strptime(start_date, '%d.%m.%Y')

    # Preparing the document with uniform margins and updated font size
    doc = Document()
    doc.preamble.append(NoEscape(r'\usepackage[table,xcdraw]{xcolor}'))
    doc.preamble.append(NoEscape(r'\usepackage{longtable}'))
    doc.preamble.append(NoEscape(r'\usepackage[left=1cm,right=2.2cm,top=1cm,bottom=1cm]{geometry}'))
    doc.preamble.append(NoEscape(r'\usepackage{setspace}'))
    doc.preamble.append(NoEscape(r'\setlength{\parindent}{0pt}'))
    doc.preamble.append(NoEscape(r'\renewcommand{\familydefault}{\sfdefault}'))
    doc.preamble.append(NoEscape(r'\pagenumbering{gobble}'))  # Disable page numbering
    doc.preamble.append(NoEscape(r'\usepackage[utf8]{inputenc}'))  # Ensure Ukrainian characters are supported
    doc.preamble.append(NoEscape(r'\usepackage[T2A]{fontenc}'))  # Load Cyrillic font encoding
    doc.preamble.append(NoEscape(r'\usepackage[ukrainian]{babel}'))  # Use Ukrainian language support

    # Setting font size for the entire document
    doc.append(NoEscape(r'\fontsize{14pt}{16pt}\selectfont'))

    # Centering the table
    doc.append(NoEscape(r'\begin{center}'))
    doc.append(NoEscape(r'\textbf{Розклад прибирання кухні на Грудень}'))

    # Creating a longtable for multi-page support
    with doc.create(LongTable(r'|p{0.3\textwidth}|p{0.55\textwidth}|p{0.15\textwidth}|')) as table:
        table.add_hline()
        table.add_row(["Номер кімнати", "Дата (День тижня, дд.мм.рр)", "Перевірка"])
        table.add_hline()
        table.end_table_header()
        table.add_hline()

        # Adding rows to the table
        room_number_index = 1
        for i in range(num_days):
            # Calculating the current date
            current_date = start_date + timedelta(days=i)

            # Calculating the room number
            room_number = (
                f"{corpus}.{floor}.{number_after_corpus}{room_number_index}"
                if room_number_index < 10
                else f"{corpus}.{floor}.{room_number_index}"
            )

            # Checking if the resident is defined
            resident = username if room_number_index == your_room_number else ""

            # Formatting the date with \hfill
            day_of_week = current_date.strftime('%A')
            date = current_date.strftime('%d.%m.%Y')
            formatted_date = NoEscape(f"{day_of_week}\\hfill {date}")

            # Adding a row to the table
            table.add_row([room_number, formatted_date, resident])
            table.add_hline()

            # Incrementing room number index
            room_number_index = (room_number_index % num_rooms) + 1

    doc.append(NoEscape(r'\end{center}'))

    # Setting the output file name for saving
    output_filename = f"Schedule/schedule_for_{corpus}_{floor}"

    # Generating the PDF
    try:
        doc.generate_pdf(output_filename, clean_tex=False)
    except Exception as e:
        print("Помилка під час генерації PDF.")
        if hasattr(e, "output"):
            print(e.output.decode("utf-8"))  # Display LaTeX error output

# Testing the function with parameters
generate_pdf_table(
    corpus="3D", 
    floor="1", 
    number_after_corpus="0", 
    num_rooms=13, 
    your_room_number=999, 
    username="rifo", 
    start_date='06.12.2024', 
    num_days=27
)
