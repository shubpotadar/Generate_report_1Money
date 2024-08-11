import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from datetime import datetime
import sys

def generate_pdf(start_date, end_date, csv_file, output_file):
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Convert DATE column to datetime, invalid parsing will be set as NaT
    df['DATE'] = pd.to_datetime(df['DATE'], format='%d/%m/%y', errors='coerce')

    # Drop rows where the DATE column is NaT (invalid dates)
    df = df.dropna(subset=['DATE'])

    # Replace empty NOTES with "-"
    df['NOTES'] = df['NOTES'].fillna('-')

    # Filter the dataframe based on the provided date range
    mask = (df['DATE'] >= start_date) & (df['DATE'] <= end_date)
    df = df[mask]

    # Remove the currency and tags columns
    df = df.drop(columns=['CURRENCY', 'CURRENCY 2', 'TAGS'])

    total_expense = 0

    # Prepare table data
    table_data = [['DATE', 'TYPE', 'FROM ACCOUNT', 'TO ACCOUNT / TO CATEGORY', 'AMOUNT', 'NOTES']]
    for _, row in df.iterrows():
        amount = row['AMOUNT']
        from_account = row['FROM ACCOUNT']
        to_account = row['TO ACCOUNT / TO CATEGORY']

        # Calculate total expense based on the criteria
        if row['TYPE'] == 'Transfer':
            pass  # pass
        else:
            total_expense += amount  # Add to total expense

        # Append the row to the table data
        table_data.append([
            row['DATE'].strftime('%d/%m/%y'), row['TYPE'], from_account, 
            to_account, f"{amount:.2f}", row['NOTES']
        ])

    # Add a row for total expense
    table_data.append(['', '', '', 'Total Expense', f"{total_expense:.2f}", ''])

    # Prepare PDF
    pdf = SimpleDocTemplate(output_file, pagesize=letter)
    elements = []

    # Add title
    styles = getSampleStyleSheet()
    title = Paragraph("Transaction Statement", styles['Title'])
    elements.append(title)
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Create table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (-2, -1), (-1, -1), colors.lightgrey),  # Highlight the total expense row
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    # Add table to PDF
    elements.append(table)
    pdf.build(elements)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python generate_statement.py <start_date> <end_date> <input_csv> <output_pdf>")
        print("Dates should be in the format: DD/MM/YY")
        sys.exit(1)

    start_date = datetime.strptime(sys.argv[1], '%d/%m/%y')
    end_date = datetime.strptime(sys.argv[2], '%d/%m/%y')
    input_csv = sys.argv[3]
    output_pdf = sys.argv[4]

    generate_pdf(start_date, end_date, input_csv, output_pdf)
