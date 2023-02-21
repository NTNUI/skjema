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
    'comment': 'Some comment\n with serveral\n newlines',
}

if len(sys.argv) < 4:
    print(f"Usage: python3 {sys.argv[0]} signature_file, attachment_files")
    print(f"Output: output.pdf")
    sys.exit(1)

# Parse the command line arguments
signature_file = sys.argv[1]
attachment_files = sys.argv[2:]

# Call the create_pdf function to generate the PDF
## create_pdf(test_data, signature_file, attachment_files)

# Call the create_pdf function to generate the PDF with base64 encoded signature

# Convert signature file to base64:image/png
with open(signature_file, "rb") as f:
    signature = f.read()
    signature = base64.b64encode(signature).decode("utf-8")
    signature = f"data:image/png;base64,{signature}"

create_pdf(test_data, signature, attachment_files)