import pdfplumber
from docx import Document
import re
from google import genai
import json
from dotenv import load_dotenv
import os
load_dotenv()


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chat = client.chats.create(model="gemini-2.0-flash")

def extract_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        
    return text

def extract_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def parse_resume(file_path):
    if file_path.endswith(".pdf"):
        text = extract_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_docx(file_path)
    else:
        return {"error": "Unsupported file type"}

    email = re.search(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', text)

    prompt = f"""
        Extract structured information from the resume below.
        Respond with ONLY a valid JSON object in this format:

        {{
          "skills": ["list of technologies"],
          "projects": [
            {{
              "name": "Project Name",
              "summary": "1-2 sentence description",
              "technologies": ["list of tools"]
            }}
          ],
          "experience": [
            {{
              "company": "Company Name",
              "title": "Job Title",
              "summary": "1-2 sentence summary",
              "technologies": ["list of tools"]
            }}
          ]
        }}

        Do NOT wrap in quotes or explain anything. Resume:
        \"\"\"{text}\"\"\"
    """

    response = chat.send_message(prompt)

    try:
        # Clean Gemini output if it's wrapped in extra quotes
        cleaned = response.text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # Print debug log
        print("Gemini response:\n", cleaned)

        # Parse the JSON
        data = json.loads(cleaned)

        return {
            "email": email.group() if email else None,
            "skills": data.get("skills", []),
            "experience": data.get("experience", []),
            "projects": data.get("projects", [])
        }

    except Exception as e:
        print("Error parsing Gemini response:", e)
        print("Raw Gemini response:\n", response.text)
        return {
            "error": str(e),
            "raw_gemini_output": response.text
        }
        
    
        
    
    