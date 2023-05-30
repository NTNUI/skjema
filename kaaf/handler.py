import base64
import logging
import os
import tempfile
import mail
import fitz
from sentry_sdk import configure_scope
import io
from PIL import Image


class UnsupportedFileException(Exception):
    pass

# Text in the PDF
field_title_map = {
    "name": "Navn:",
    "mailfrom": "E-post:",
    "committee": "Gruppe/utvalg:",
    "occasion": "Anledning/arrangement:",
    "date": "Reise startdato:",
    "dateEnd": "Reise sluttdato:",
    "destination": "Reisedestinasjon:",
    "travelMode": "Reisemåte:",
    "route": "Reiserute:",
    "distance": "Antall kilometer:",
    "team": "Reisefølge:",
    "numberOfTravelers": "Antall reisende:",
    "accountNumber": "Kontonummer:",
    "amount": "Beløp:",
    "maxRefund": "(Autogenerert) Maks HS støtte:",
    "comment": "Kommentar:",
}

temporary_files = []


def data_is_valid(data):
    fields = [
        "name",
        "mailfrom",
        "committee",
        "mailto",
        "occasion",
        "date",
        "dateEnd",
        "destination",
        "travelMode",
        "route",
        "distance",
        "team",
        "numberOfTravelers",
        "accountNumber",
        "amount",
        "signature",
        "images",
    ]
    return [f for f in fields if f not in data or len(data[f]) == 0]


def data_to_str(data, field_title_map):
    left_column = []
    right_column = []

    for key, title in field_title_map.items():
        if key in data:
            left_column.append(f"{title}")
            right_column.append(f"{data[key]}")

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

def add_page_number(page, page_number, total_pages):
    footer_text = f"Side {page_number} av {total_pages}"
    fontsize = 9
    fontname = "Helvetica"
    
    # Measure the width of the rendered footer_text
    font = fitz.Font(fontname)
    text_width = font.text_length(footer_text, fontsize)

    footer_position = fitz.Point(
        (page.rect.width - text_width) / 2,
        page.rect.height - 30
    )
    page.insert_text(
        footer_position, footer_text, fontname=fontname, fontsize=fontsize
    )


def calculate_traveling_refund(data):
    try:
        distance = float(data["distance"].replace(",", "."))
        numberOfTravelers = int(data["numberOfTravelers"])
        amount = float(data["amount"].replace(",", "."))

        res = (distance * 2 * 0.9 * numberOfTravelers) / 2
        if((amount / 2) < res):
            res = amount / 2

        amount_pr_person = res / numberOfTravelers

        if(amount_pr_person <= 200):
            res = 0
        if(amount_pr_person >= 1500):
            res = 1500 * numberOfTravelers
            
        return str(res)
    except Exception as e:
        print(e)
        return f"Noe gikk galt ved utregning av reisestøtte", 500


def create_pdf(data, signature=None, images=None):
    doc = fitz.open()
    page = doc.new_page()

    page.insert_text(
        fitz.Point(50, 75), "Reiseregningsskjema", fontname="Helvetica-Bold", fontsize=24
    )

    logo = fitz.Pixmap("images/ntnui.png")
    page.insert_image(fitz.Rect(425, 40, 525, 90), pixmap=logo)

    # Add the input values in a two-column layout
    left_text, right_text = data_to_str(data, field_title_map)
    page.insert_text(
        fitz.Point(50, 150), left_text, fontname="Helvetica-Bold", fontsize=11
    )
    page.insert_text(
        fitz.Point(240, 150), right_text, fontname="Helvetica", fontsize=11
    )

    # Add the signature image
    if signature is None:
        raise RuntimeError("No signature provided")
    if signature.startswith("data:image"):
        signature = base64_to_file(signature.split(",")[1])
    page.insert_text(
        fitz.Point(50, page.bound().height * 0.75),  # Adjusted to 75% from top.
        "Signatur:",
        fontname="Helvetica-Bold",
        fontsize=12,
    )
    signature_pixmap = fitz.Pixmap(signature)
    signature_rect = fitz.Rect(
        50, 
        page.bound().height * 0.75,  # Adjusted to 75% from top.
        550, 
        min(page.bound().height * 1.0, page.bound().height - 1)  # Adjusted to not exceed the page height.
    )
    page.insert_image(signature_rect, pixmap=signature_pixmap)


    # Add the remaining pages with the receipt attachments
    if images is None:
        raise RuntimeError("No images provided")
    if not isinstance(images, list):
        images = [images]
    for attachment in images:
        # Get file type from base64 string
        if not "image/" in attachment and not "application/pdf" in attachment:
            raise UnsupportedFileException(
                f"Unsupported file type in base64 string: {attachment[:30]}"
            )
        parts = attachment.split(";base64,")
        file_type = (
            "pdf" if "application/pdf" in attachment else parts[0].split("image/")[1]
        )
        attachment = base64_to_file(parts[1])
        if file_type == "pdf":
            pdf_doc = fitz.open(attachment)
            for i in range(pdf_doc.page_count):
                page = doc.new_page()
                page.show_pdf_page(fitz.Rect(0, 0, 612, 792), pdf_doc, i)
            pdf_doc.close()
        elif file_type in ["jpg", "jpeg", "png", "gif"]:
            page = doc.new_page()
            pixmap = fitz.Pixmap(attachment)
            page.insert_image(page.rect, pixmap=pixmap)
        ## TODO: HEIC is received as application/octet-stream, not as image/heic
        # elif file_type == 'heic':
        #     heif_image = pyheif.read(attachment)
        #     png_image = Image.frombytes(
        #         heif_image.mode,
        #         heif_image.size,
        #         heif_image.data,
        #         "raw",
        #         heif_image.mode,
        #         heif_image.stride,
        # )
        #     png_bytes = io.BytesIO()
        #     png_image.save(png_bytes, format="PNG")
        #     width, height = png_image.size
        #     samples = png_image.tobytes()
        #     pixmap = fitz.Pixmap(fitz.csRGB, width, height, samples)
        #     page.insert_image(page.rect, pixmap=pixmap)
        else:
            raise UnsupportedFileException(
                f"Unsupported file type: {file_type}. Use pdf, jpg, jpeg or png"
            )

    # Add page numbers to all pages
    for i, page in enumerate(doc):
        add_page_number(page, i + 1, doc.page_count)

    # Save the PDF document
    doc.save("output.pdf")
    with open("output.pdf", "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
    doc.close()
    for f in temporary_files:
        os.remove(f)
        temporary_files.remove(f)
    return pdf_bytes  # Return the PDF document as bytes


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
    
    data["amount"] = data["amount"].replace(".", ",") # Norwegian standard is comma as decimal separator
    data["maxRefund"] = calculate_traveling_refund(data)
    data["comment"] = data["comment"].replace("\n", "  ") # Strip newlines from comment
    # If comment is longer than 50 characters, add newline after every 50 characters to avoid overflowing the pdf
    if len(data["comment"]) > 50:
        data["comment"] = "\n".join(
            data["comment"][i : i + 50] for i in range(0, len(data["comment"]), 50)
        )

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
    return "Reiseregning generert og sendt til kasserer!", 200
