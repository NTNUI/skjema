import argparse
import base64
import sys

from handler import create_pdf

test_data = {
    'name': 'John Doe',
    'mailfrom': 'johndoe@ntnui.dev',
    'committee': 'Sprint',
    'accountNumber': '123456789',
    'amount': '69.69',
    'date': '2023-05-17',
    'occasion': 'Expense reimbursement',
    'comment': 'Some comment\n with a newline',
}

if len(sys.argv) < 4:
    print(f"Usage: python3 {sys.argv[0]} signature.png output.pdf attachment1.png attachment2.pdf")
    sys.exit(1)

# Parse the command line arguments
output_file = sys.argv[1]
signature_file = sys.argv[2]
attachment_files = sys.argv[3:]

# Call the create_pdf function to generate the PDF
create_pdf(test_data, output_file, signature_file, attachment_files)