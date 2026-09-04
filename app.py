from pdf_parser import extract_text_from_pdf
from text_cleaner import clean_text
pdf_path = "C:\\Users\\SAMA\\Downloads\\resume-ai\\resume\\NeelimaSingh_CSE_AI_2028.pdf"

pages = extract_text_from_pdf(pdf_path)

full_text = ""

for page in pages:
    full_text += page["text"] + "\n"

cleaned_text = clean_text(full_text)


with open("resume.txt", "w", encoding="utf-8") as file:
    file.write(cleaned_text)
print("Resume successfully converted to text!")