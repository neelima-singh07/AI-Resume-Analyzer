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


# -----------------------------
# CREATE CHUNK EMBEDDINGS
# -----------------------------

chunk_embeddings = model.encode(resume_chunks)

print("Chunk embeddings shape:", chunk_embeddings.shape)


MATCH_THRESHOLD = 0.50
PARTIAL_THRESHOLD = 0.35

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

    if best_score >= MATCH_THRESHOLD:
        status = "MATCHED"

    elif best_score >= PARTIAL_THRESHOLD:
        status = "PARTIAL"

    else:
        status = "MISSING"

    results.append({
        "requirement": requirement,
        "score": float(best_score),
        "status": status,
        "matched_chunk": matched_chunk
    })

    print(f"\nRequirement: {requirement}")
    print(f"Score: {best_score:.4f}")
    print(f"Status: {status}")
    print(f"Evidence: {matched_chunk}")