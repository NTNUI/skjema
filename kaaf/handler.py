import base64
import logging
import os
import tempfile
import mail
import fitz
from sentry_sdk import configure_scope
import pyheif
import io
from PIL import Image

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

temporary_files = []

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
    left_column = []
    right_column = []

    for key, value in data.items():
        left_column.append(f"{field_title_map[key]}")
        right_column.append(f"{value}")

    left_text = "\n\n".join(left_column)
    right_text = "\n\n".join(right_column)

    return left_text, right_text


# Decode the base64 string and save it to a temporary file
def base64_to_file(base64_string):
    # Decode the base64 string
    decoded = base64.b64decode(base64_string)
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temporary_files.append(temp_file.name)
    # Write the decoded data to the temporary file
    temp_file.write(decoded)
    # Close the file
    temp_file.close()
    # Return the path to the temporary file
    return temp_file.name

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

    # Add the input values in a two-column layout
    left_text, right_text = data_to_str(data, field_title_map)
    page.insert_text(fitz.Point(50, 200), left_text, fontname="Helvetica-Bold", fontsize=12)
    page.insert_text(fitz.Point(300, 200), right_text, fontname="Helvetica", fontsize=12)

    # Add the signature image
    if signature is None:
        raise RuntimeError("No signature provided")
    # Create an image from signature and add it to the page
    if signature.startswith("data:image"):
        signature = base64_to_file(signature.split(",")[1])
    page.insert_text(fitz.Point(50, page.bound().height * 0.67), "Signatur:", fontname="Helvetica-Bold", fontsize=12)
    signature_pixmap = fitz.Pixmap(signature)
    signature_rect = fitz.Rect(50, page.bound().height * 0.67, 550, page.bound().height * 0.97)
    page.insert_image(signature_rect, pixmap=signature_pixmap)

    # Add the remaining pages with the receipt attachments
    if images is None:
        raise RuntimeError("No images provided")
    if not isinstance(images, list):
        images = [images]
    for attachment in images:
        page = doc.new_page()
        # Get file type from base64 string
        if not "image/" in attachment and not "application/pdf" in attachment:
            raise UnsupportedFileException(f"Unsupported file type in base64 string: {attachment[:30]}")
        parts = attachment.split(";base64,")
        file_type = "pdf" if "application/pdf" in attachment else parts[0].split("image/")[1]
        attachment = base64_to_file(parts[1])
        if file_type == 'pdf':
            pdf_doc = fitz.open(attachment)
            page.show_pdf_page(fitz.Rect(0, 0, 612, 792), pdf_doc, 0)
            pdf_doc.close()
        elif file_type in ['jpg', 'jpeg', 'png', 'gif']:
            pixmap = fitz.Pixmap(attachment)
            page.insert_image(page.rect, pixmap=pixmap)
        elif file_type == 'heic':
            heif_image = pyheif.read(attachment)
            png_image = Image.frombytes(
                heif_image.mode, 
                heif_image.size, 
                heif_image.data,
                "raw",
                heif_image.mode,
                heif_image.stride,
        )
            png_bytes = io.BytesIO()
            png_image.save(png_bytes, format="PNG")
            width, height = png_image.size
            samples = png_image.tobytes()
            pixmap = fitz.Pixmap(fitz.csRGB, width, height, samples)
            page.insert_image(page.rect, pixmap=pixmap)
        else:
            raise UnsupportedFileException(f"Unsupported file type: {file_type}. Use pdf, jpg, jpeg or png")

    # Save the PDF document
    doc.save("last_output.pdf")
    doc.close()
    for f in temporary_files:
        os.remove(f)
        temporary_files.remove(f)
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
