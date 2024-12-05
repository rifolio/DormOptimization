from pylatex import Document, LongTable, NoEscape
from datetime import datetime, timedelta

def generate_pdf_table(num_rooms, start_date, num_days, output_filename):
    # Generates a PDF file with a table that maps room numbers to corresponding dates for given number of days and initial date

    # getting the start date
    start_date = datetime.strptime(start_date, '%d.%m.%Y')
    
    # gettin ready the document
    doc = Document()
    doc.preamble.append(NoEscape(r'\usepackage[table,xcdraw]{xcolor}'))
    doc.preamble.append(NoEscape(r'\usepackage{longtable}'))

    # Just some basic info on top of the table, optional
    # doc.append(NoEscape(r'Schedule'))
    # doc.append(NoEscape(r'\vspace{10pt}'))  # Add spacing after the text

    # LongTable in case we have more than 30 days
    with doc.create(LongTable(r'|p{0.3\textwidth}|p{0.6\textwidth}|p{0.1\textwidth}|')) as table:
        table.add_hline()
        table.add_row(["Room Number", "Date (Day of the Week, dd.mm.yy)", "Checkin"])
        table.add_hline()
        table.end_table_header()
        
        # adding table rows
        for i in range(num_days):
            room_number = f"3D.1.0{(i % num_rooms) + 1}"
            current_date = start_date + timedelta(days=i)
            day_of_week = current_date.strftime('%A')
            date = current_date.strftime('%d.%m.%Y')
            
            # to make it more pretty using \hfill to push the date to the right border inside the column
            formatted_date = NoEscape(f"{day_of_week}\\hfill{date}")
            
            table.add_row([room_number, formatted_date, ""])
            table.add_hline()

    # generate PDF
    doc.generate_pdf(output_filename, clean_tex=False)

# testing method
generate_pdf_table(num_rooms=13, start_date='05.12.2024', num_days=60, output_filename='room_schedule')
