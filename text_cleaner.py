import re
def clean_text(text):
    # Multiple spaces ko single space
    text = re.sub(r'\s+', ' ', text)

    # Starting/ending spaces remove
    text = text.strip()

    return text
