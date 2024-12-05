from pylatex import Document, LongTable, NoEscape
from datetime import datetime, timedelta
import holidays

def generate_pdf_table(corpus, floor, number_after_corpus, num_rooms, your_room_number, username, start_date, num_days):
    # generates a PDF file with a table that maps room numbers to corresponding dates and residents
    
    # getting holidays using the holidays library
    dk_holidays = holidays.CountryHoliday('DK', years=[2024, 2025])
    
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
    doc.append(NoEscape(r'Kitchen Cleaning for December'))

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
            
            # check if the current date is a holiday
            if current_date in dk_holidays:
                holiday_name = dk_holidays.get(current_date)
                # add a row for holidays with the holiday name
                holidate = NoEscape(f"{current_date.strftime('%A')} \\hfill {current_date.strftime('%d.%m.%Y')}")
                table.add_row([holiday_name, holidate, ""])
                table.add_hline()
                continue
            
            # calculating the room number
            room_number = (
                f"{corpus}.{floor}.{number_after_corpus}{room_number_index}"
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

    # setting the output file name dynamically
    output_filename = f"Schedule/schedule_for_{corpus}_{floor}"

    # generating the PDF
    try:
        doc.generate_pdf(output_filename, clean_tex=False)
    except Exception as e:
        print("Error generating PDF.")
        if hasattr(e, "output"):
            print(e.output.decode("utf-8"))  # display the LaTeX error output

# testing the method with inputs
generate_pdf_table(
    corpus="3D", 
    floor="1", 
    number_after_corpus="0", 
    num_rooms=13, 
    your_room_number=999, 
    username="rifo", 
    start_date='06.12.2024', 
    num_days=365
)
