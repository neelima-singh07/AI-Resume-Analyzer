import re


def jd_read(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        jd_text = file.read()

    return jd_text

def clean_jd(jd_text):

    # Extra spaces remove
    jd_text = re.sub(r'[ \t]+', ' ', jd_text)

    # Extra blank lines remove
    jd_text = re.sub(r'\n+', '\n', jd_text)

    return jd_text.strip()


def extract_sections(jd_text):

    lines = jd_text.split("\n")

    requirements = []
    responsibilities = []

    current_section = None

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if line.lower() == "requirements:":
            current_section = "requirements"
            continue

        if line.lower() == "responsibilities:":
            current_section = "responsibilities"
            continue

        if current_section == "requirements":
            requirements.append(line)

        elif current_section == "responsibilities":
            responsibilities.append(line)

    return requirements, responsibilities
