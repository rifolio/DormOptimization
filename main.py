from pylatex import Document, LongTable, NoEscape
from datetime import datetime, timedelta

def generate_pdf_table(corpus, floor, number_after_corpus, num_rooms, your_room_number, username, start_date, num_days):
    # generates a PDF file with a table that maps room numbers to corresponding dates and residents
    
    # parsing the start date
    start_date = datetime.strptime(start_date, '%d.%m.%Y')
    
    # preparing the document
    doc = Document()
    doc.preamble.append(NoEscape(r'\usepackage[table,xcdraw]{xcolor}'))
    doc.preamble.append(NoEscape(r'\usepackage{longtable}'))

    # creating a longtable for multi-page support
    with doc.create(LongTable(r'|p{0.25\textwidth}|p{0.5\textwidth}|p{0.1\textwidth}|p{0.15\textwidth}|')) as table:
        table.add_hline()
        table.add_row(["Room Number", "Date (Day of the Week, dd.mm.yy)", "Checkin", "Residents"])
        table.add_hline()
        table.end_table_header()
        
        # adding table rows
        for i in range(num_days):
            # calculating the room number
            room_number_index = (i % num_rooms) + 1
            room_number = (
                f"{corpus}.{floor}.{number_after_corpus}{room_number_index}"
                if room_number_index < 10
                else f"{corpus}.{floor}.{room_number_index}"
            )
            
            # checking if the current room is the user's room
            resident = username if room_number_index == your_room_number else ""
            
            # formatting the date with alignment
            current_date = start_date + timedelta(days=i)
            day_of_week = current_date.strftime('%A')
            date = current_date.strftime('%d.%m.%Y')
            formatted_date = NoEscape(f"{day_of_week}\\hfill{date}")
            
            # adding a row to the table
            table.add_row([room_number, formatted_date, "", resident])
            table.add_hline()

    # setting the output file name dynamically
    output_filename = f"Schedule/schedule_for_{corpus}.{floor}.pdf"

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
    floor="2", 
    number_after_corpus="0", 
    num_rooms=13, 
    your_room_number=4, 
    username="Vlad,Dmytro", 
    start_date='05.12.2024', 
    num_days=720
)
