import argparse
import base64
import sys
import os
import magic

from handler import create_pdf

test_data = {
    "name": "John Doe",
    "mailfrom": "johndoe@ntnui.dev",
    "committee": "Sprint",
    "accountNumber": "123456789",
    "amount": "69.69",
    "date": "2023-05-17",
    "occasion": "Expense reimbursement",
    "comment": "Some comment\n with multiple\n newlines",
}

if len(sys.argv) < 3:
    print("Error: Missing arguments")
    print(f"Usage: python3 {sys.argv[0]} signature_file, attachment_files")
    print(f"Output: output.pdf")
    sys.exit(1)

# Parse the command line arguments
signature_file = sys.argv[1]
attachment_files = sys.argv[2:]

allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".heic"}


def is_valid_file_extension(file_path, allowed_extensions):
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower() in allowed_extensions


# Return exception if signature or attachment files are not valid
if not is_valid_file_extension(signature_file, allowed_extensions):
    raise Exception(f"Invalid signature file extension: {signature_file}")
for file_path in attachment_files:
    if not is_valid_file_extension(file_path, allowed_extensions):
        raise Exception(f"Invalid attachment file extension: {file_path}")

# Convert signature file to base64:image/png
with open(signature_file, "rb") as f:
    signature = f.read()
    signature = base64.b64encode(signature).decode("utf-8")
    signature = f"data:image/png;base64,{signature}"

# Check file type and convert attachment files to base64 with MIME type
attachments = []
for file_path in attachment_files:
    with open(file_path, "rb") as f:
        # Read the file as bytes
        file_data = f.read()

        # Detect the filetype using python-magic
        file_type = magic.from_buffer(file_data, mime=True)

        # Convert the file data to base64
        file_data = base64.b64encode(file_data).decode("utf-8")

        # Add the filetype prefix to the base64 string
        file_data = f"data:{file_type};base64,{file_data}"

        # Check if the filetype is one of the allowed ones
        allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/heic"]
        if file_type in allowed_types:
            # Append the file data to the attachments list
            attachments.append(file_data)

print(f"Signature: {signature[:50]}")
for attachment in attachments:
    print(f"Attachment: {attachment[:50]}")

# Call the create_pdf function to generate the PDF
create_pdf(test_data, signature, attachments)
