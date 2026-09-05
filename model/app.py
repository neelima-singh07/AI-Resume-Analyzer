from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pdf_parser import extract_text_from_pdf

from job.jd_processor import jd_read, extract_sections
model = SentenceTransformer("all-MiniLM-L6-v2")
jd = jd_read("C:\\Users\\SAMA\\Downloads\\resume-ai\\job\\job_description.txt")
requirements, responsibilities = extract_sections(jd)

pages = extract_text_from_pdf(
    r"C:\Users\SAMA\Downloads\resume-ai\resume\NeelimaSingh_CSE_AI_2028.pdf"
)


full_text = ""

for page in pages:
    full_text += page["text"] + "\n"


# Overall resume embedding
#resume_embedding = model.encode([full_text])

#


# -----------------------------
# CREATE RESUME CHUNKS
# -----------------------------

import re

def create_chunks(text):

    lines = text.split("\n")

    sections = [
        "Education",
        "Experience",
        "Projects",
        "Technical Skills",
        "Achievements",
        "Coding Profile"
    ]

    current_section = "General"

    chunks = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Check if line is a section heading
        if line in sections:
            current_section = line
            continue

        # Remove bullet symbols
        line = re.sub(r"^[•–-]\s*", "", line)

        # Ignore very short lines
        if len(line) < 10:
            continue

        # Add section context
        chunk = f"{current_section} | {line}"

        chunks.append(chunk)

    return chunks

resume_chunks = create_chunks(full_text)


print("\nNumber of chunks:", len(resume_chunks))

print("\nChecking SQL in resume...")

print("SQL in full text:", "SQL" in full_text.upper())

for i, chunk in enumerate(resume_chunks):
    if "SQL" in chunk.upper():
        print(f"\nSQL found in Chunk {i + 1}:")
        print(chunk)
# -----------------------------
# CREATE CHUNK EMBEDDINGS
# -----------------------------

chunk_embeddings = model.encode(resume_chunks)

print("Chunk embeddings shape:", chunk_embeddings.shape)


MATCH_THRESHOLD = 0.50
PARTIAL_THRESHOLD = 0.30

SKILL_ALIASES = {
    "python": ["python"],
    "machine learning": ["machine learning", "ml", "scikit-learn", "sklearn"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "nlp": ["nlp", "natural language processing"],
}


def find_skill_alias(requirement, text):
    aliases = SKILL_ALIASES.get(
        requirement.strip().lower(),
        [requirement.strip().lower()]
    )

    for alias in aliases:
        match = re.search(rf"\b{re.escape(alias)}\b", text, re.IGNORECASE)

        if match:
            return alias

    return None

results = []

for requirement in requirements:

    jd_embedding = model.encode([requirement])

    similarities = cosine_similarity(
        jd_embedding,
        chunk_embeddings
    )

    best_index = similarities[0].argmax()
    best_score = similarities[0][best_index]

    matched_chunk = resume_chunks[best_index]
    matched_alias = find_skill_alias(requirement, full_text)

    if matched_alias:
        status = "MATCHED"
        final_score = 1.0

        for chunk in resume_chunks:
            if re.search(rf"\b{re.escape(matched_alias)}\b", chunk, re.IGNORECASE):
                matched_chunk = chunk
                break

    elif best_score >= MATCH_THRESHOLD:
        status = "MATCHED"
        final_score = float(best_score)

    elif best_score >= PARTIAL_THRESHOLD:
        status = "PARTIAL"
        final_score = float(best_score)

    else:
        status = "MISSING"
        final_score = float(best_score)

    results.append({
        "requirement": requirement,
        "score": final_score,
        "status": status,
        "matched_chunk": matched_chunk,
        "matched_alias": matched_alias,
    })

    print(f"\nRequirement: {requirement}")
    print(f"Score: {final_score:.4f}")
    print(f"Status: {status}")
    print(f"Evidence: {matched_chunk}")

matched_points = sum(result["status"] == "MATCHED" for result in results)
partial_points = sum(result["status"] == "PARTIAL" for result in results) * 0.5
match_percentage = ((matched_points + partial_points) / len(results)) * 100

print(f"\nOverall match score: {match_percentage:.1f}%")