
#enumerate(doc) hume page ka index + page object deta hai.
import fitz
def extract_text_from_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(doc):

        text = page.get_text()

        pages.append({
            "page": page_number + 1,
            "text": text
        })

    doc.close()

    return pages