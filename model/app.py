import os
from pathlib import Path
import re

from dotenv import load_dotenv
from google import genai
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from pdf_parser import extract_text_from_pdf

from job.jd_processor import jd_read, extract_sections, clean_jd

load_dotenv(Path(__file__).with_name(".env"))

model = SentenceTransformer("all-MiniLM-L6-v2")
jd = jd_read("C:\\Users\\SAMA\\Downloads\\resume-ai\\job\\job_description.txt")
jd=clean_jd(jd)
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

def find_exact_skill(requirement, text):
    pattern = rf"(?<!\w){re.escape(requirement.strip())}(?!\w)"
    return re.search(pattern, text, re.IGNORECASE)

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
    matched_skill = find_exact_skill(requirement, full_text)

    if matched_skill:
        status = "MATCHED"
        final_score = 1.0

        for chunk in resume_chunks:
            if find_exact_skill(requirement, chunk):
                matched_chunk = chunk
                break

    elif len(requirement.split()) == 1:
        status = "MISSING"
        final_score = 0.0

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
        "matched_skill": matched_skill.group(0) if matched_skill else None,
    })

    print(f"\nRequirement: {requirement}")
    print(f"Score: {final_score:.4f}")
    print(f"Status: {status}")
    print(f"Evidence: {matched_chunk}")

matched_points = sum(result["status"] == "MATCHED" for result in results)
partial_points = sum(result["status"] == "PARTIAL" for result in results) * 0.5
match_percentage = ((matched_points + partial_points) / len(results)) * 100

print(f"\nOverall match score: {match_percentage:.1f}%")


def generate_explanation(results, match_percentage):
    matched = [item["requirement"] for item in results if item["status"] == "MATCHED"]
    partial = [item["requirement"] for item in results if item["status"] == "PARTIAL"]
    missing = [item["requirement"] for item in results if item["status"] == "MISSING"]

    def local_explanation():
        if match_percentage >= 75:
            fit = "strong fit"
        elif match_percentage >= 50:
            fit = "moderate fit"
        else:
            fit = "limited fit"

        explanation = (
            f"You are a {fit} for this role with an overall match score of "
            f"{match_percentage:.1f}%."
        )
        if matched:
            explanation += f" Your matching strengths include: {', '.join(matched)}."
        if partial:
            explanation += f" These areas are partially aligned: {', '.join(partial)}."
        if missing:
            explanation += f" Missing requirements to improve are: {', '.join(missing)}."
        return explanation

    prompt = f"""You are a professional resume evaluator.

Give a concise, honest explanation of the candidate's fit for the job based only on
the structured matching results below. Do not invent skills, experience, or claims.
Mention the overall fit, matched strengths, partial matches, and missing skills.
Use simple professional English and keep the response under 120 words.

Overall score: {match_percentage:.1f}%
Matched requirements: {matched or "None"}
Partial requirements: {partial or "None"}
Missing requirements: {missing or "None"}
"""

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return local_explanation()

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as error:
        return local_explanation() + f" AI explanation was unavailable because of a Gemini API error: {error}"


print("\nExplanation:")
print(generate_explanation(results, match_percentage))