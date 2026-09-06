# Resume AI Matcher

A Python project that extracts resume text from a PDF, compares it with job-description requirements, and generates a readable fit explanation.

## Features

- Extracts resume text from a PDF using PyMuPDF.
- Reads requirements and responsibilities from a job description.
- Creates resume text chunks with section context.
- Uses `all-MiniLM-L6-v2` embeddings for semantic comparison.
- Uses exact, boundary-safe matching for skills and single-word requirements.
- Generates a user-facing explanation with the Gemini API.
- Uses a local explanation fallback if the Gemini API is unavailable.

## Project Structure

```text
resume-ai/
|-- app.py                 # Extracts and cleans resume PDF text
|-- pdf_parser.py          # PDF text extraction helper
|-- text_cleaner.py        # Resume text cleanup
|-- resume.txt             # Generated cleaned resume text
|-- requirements.txt       # Python dependencies
|-- .env                   # Local API key; do not commit
|-- job/
|   |-- app.py             # Prints parsed job requirements
|   |-- jd_processor.py    # Reads, cleans, and parses the job description
|   |-- job_description.txt
|-- model/
    |-- app.py             # Main matching and explanation pipeline
    |-- embedding_model.py # Reusable embedding helper
    |-- .env               # API key location used by model/app.py
```

## Setup

Create or activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
.\venv\Scripts\pip.exe install -r requirements.txt
```

## Gemini API Key

The current model script loads the key from `model/.env`.

Create or update `model/.env`:

```env
GEMINI_API_KEY=your-gemini-api-key
```

`GOOGLE_API_KEY` is also supported as a fallback variable name.

Never commit the key. The repository `.gitignore` excludes `.env` files. If a key is exposed, revoke it and create a new one.

## Running the Project

Run the complete resume matching flow from the project root:

```powershell
.\venv\Scripts\python.exe -m model.app
```

The script will:

1. Load the job description.
2. Extract its requirements and responsibilities.
3. Extract text from the resume PDF.
4. Create contextual resume chunks.
5. Generate embeddings for resume chunks and requirements.
6. Match each requirement and print evidence.
7. Calculate the overall match percentage.
8. Ask Gemini to write a concise fit explanation.

To only test resume-to-text conversion:

```powershell
.\venv\Scripts\python.exe app.py
```

To print parsed job-description sections:

```powershell
.\venv\Scripts\python.exe job/app.py
```

## Matching Logic

The matcher uses a hybrid approach:

- Exact requirement matching is checked first with safe token boundaries.
- An unmatched single-word requirement is marked `MISSING` instead of relying on semantic similarity.
- Multi-word requirements can use MiniLM cosine similarity as a fallback.
- Scores are classified using these thresholds:
  - `>= 0.50`: `MATCHED`
  - `>= 0.35`: `PARTIAL`
  - `< 0.35`: `MISSING`

This keeps exact technical skills reliable while allowing semantic matching for concepts such as `Data Analysis` or `Machine Learning`.

## Explanation Generation

The Gemini API receives only structured matching results, including:

- Overall match percentage
- Matched requirements
- Partial requirements
- Missing requirements

The API does not decide whether a skill matches. The Python matching logic remains the source of truth. If the API key is missing or the request fails, the script prints a local rule-based explanation.

## Notes

- Resume and job-description paths are currently configured in the Python scripts.
- The resume PDF is ignored by Git through `.gitignore`.
- Do not use this prototype as the sole basis for automated hiring decisions.
