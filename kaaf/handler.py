import base64
import logging
import io
import tempfile
import mail
import functools
import operator

import fitz

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

def create_pdf(data, output_file, signature, images):

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
    signature_pixmap = fitz.Pixmap(signature)
    signature_rect = fitz.Rect(50, page.bound().height * 0.67, 550, page.bound().height * 0.97)
    page.insert_image(signature_rect, pixmap=signature_pixmap)

    # Add the remaining pages with the receipt attachments
    for attachment in images:
        page = doc.new_page()
        file_type = attachment.split('.')[-1]
        if file_type == 'pdf':
            pdf_doc = fitz.open(attachment)
            page.show_pdf_page(fitz.Rect(0, 0, 612, 792), pdf_doc, 0)
            pdf_doc.close()
        elif file_type in ['jpg', 'jpeg', 'png']:
            pixmap = fitz.Pixmap(attachment)
            page.insert_image(fitz.Rect(50, 50, 550, 1000), pixmap=pixmap)

    # Save the PDF document
    doc.save(output_file)
    doc.close()


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

    #try:
    #    data = modify_data(data)
    #except UnsupportedFileException as e:
    #    logging.error(f"Unsupported file type: {e}")
    #    return (
    #        "En av filene som ble lastet opp er ikke i støttet format. Bruk PNG, JPEG, GIF, HEIC eller PDF",
    #        400,
    #    )

    try:
        file = create_pdf(data)
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
