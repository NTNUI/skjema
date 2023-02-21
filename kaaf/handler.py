import base64
import logging
import io
import os
import tempfile
import mail
import functools
import operator
import fitz
from sentry_sdk import configure_scope

class UnsupportedFileException(Exception):
    pass


field_title_map = {
    "name": "Navn:",
    "mailfrom": "E-post:",
    "committee": "Gruppe/utvalg:",
    "accountNumber": "Kontonummer:",
    "amount": "Beløp:",
    "date": "Dato:",
    "occasion": "Anledning/arrangement:",
    "comment": "Kommentar:",
}


def data_is_valid(data):
    fields = [
        "name",
        "mailfrom",
        "committee",
        "mailto",
        "accountNumber",
        "amount",
        "date",
        "occasion",
        "signature",
        "images",
    ]
    return [f for f in fields if f not in data or len(data[f]) == 0]


def data_to_str(data, field_title_map):
    result = ""
    for key, value in data.items():
        result += f"{field_title_map.get(key, key)} {value}\n"
    return result

def base64_to_file(data):
    data = io.BytesIO(base64.b64decode(data))
    signature_data = data.read().decode("utf-8")
    return base64.b64decode(signature_data)

def create_pdf(data, signature=None, images=None):

    # Create a new PDF document
    doc = fitz.open()
    # Add the first page with the input values and the signature
    page = doc.new_page()
    height = page.bound().height

    # Add logo to the top left corner
    logo = fitz.Pixmap("images/ntnui.png")
    page.insert_image(fitz.Rect(50, 50, 200, 100), pixmap=logo)

    # Add the title below the logo
    page.insert_text(fitz.Point(50, 150), "Refusjonsskjema", fontname="Helvetica-Bold", fontsize=24)

    # Add the input values
    page.insert_text(fitz.Point(50, 200), data_to_str(data, field_title_map), fontname="Helvetica", fontsize=12)
    
    # Add the signature image
    if signature is None:
        raise RuntimeError("No signature provided")
    # Create an image from signature and add it to the page
    if signature.startswith("data:image"):
        signature = base64_to_file(signature.split(",")[1])
    signature_pixmap = fitz.Pixmap(signature)
    signature_rect = fitz.Rect(50, page.bound().height * 0.67, 550, page.bound().height * 0.97)
    page.insert_image(signature_rect, pixmap=signature_pixmap)

    # Add the remaining pages with the receipt attachments
    if images is None:
        raise RuntimeError("No images provided")
    for attachment in images:
        page = doc.new_page()
        if attachment.startswith("data:image"):
            attachment = base64_to_file(attachment.split(",")[1])
        file_type = attachment.split('.')[-1]
        if file_type == 'pdf':
            pdf_doc = fitz.open(attachment)
            page.show_pdf_page(fitz.Rect(0, 0, 612, 792), pdf_doc, 0)
            pdf_doc.close()
        elif file_type in ['jpg', 'jpeg', 'png']:
            pixmap = fitz.Pixmap(attachment)
            page.insert_image(fitz.Rect(50, 50, 550, 1000), pixmap=pixmap)
        else:
            raise UnsupportedFileException(f"Unsupported file type: {file_type}. Use pdf, jpg, jpeg or png")

    # Save the PDF document
    doc.save("output.pdf")
    doc.close()
    return doc


def handle(data):
    # Add some info about the user to the scope
    with configure_scope() as scope:
        scope.user = {
            "name": data["name"],
            "mailfrom": data["mailfrom"],
            "mailto": data["mailto"],
        }
    req_fields = data_is_valid(data)
    if len(req_fields) > 0:
        return f'Requires fields {", ".join(req_fields)}', 400

    try:
        file = create_pdf(data, data["signature"], data["images"])
        mail.send_mail([data["mailto"], data["mailfrom"]], data, file)
    except RuntimeError as e:
        logging.warning(f"Failed to generate pdf with exception: {e}")
        return f"Klarte ikke å generere pdf: {e}", 500
    except mail.MailConfigurationException as e:
        logging.warning(f"Failed to send mail: {e}")
        return f"Klarte ikke å sende email: {e}", 500
    except Exception as e:
        logging.error(f"Failed with exception: {e}")
        return f"Noe uventet skjedde: {e}", 400

    logging.info("Successfully generated pdf and sent mail")
    return "Refusjonsskjema generert og sendt til kasserer!", 200
