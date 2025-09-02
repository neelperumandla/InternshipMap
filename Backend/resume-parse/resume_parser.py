import pdfplumber
from docx import Document
import re
from google import genai
import json
from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain.vectorstores import Chroma
import chromadb

load_dotenv()

llm = GoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
# embedding = OllamaEmbeddings(model='llama3')
# CHROMA_DIR = "database/chroma"
# if os.path.exists(CHROMA_DIR):
#     vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding)
# else:
#     vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding)
# retriever = vectorstore.as_retriever()

# chroma_client = chromadb.Client()
# collection = chroma_client.get_or_create_collection("resumes")
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# chat = client.chats.create(model="gemini-2.0-flash")

def extract_pdf(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    text = ""
    
    for page in pages:
        content = page.page_content
        if content:
            text += content + "\n"
        
    return text

def extract_docx(file_path):
    loader = Docx2txtLoader(file_path)
    documents = loader.load_and_split()
    return "\n".join([para.page_content for para in documents])

def parse_resume(file_path, user_email):
    if file_path.endswith(".pdf"):
        text = extract_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_docx(file_path)
    else:
        return {"error": "Unsupported file type"}

    # email = re.search(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', text)

    parse_prompt_template = ChatPromptTemplate.from_template(
    """You are given this resume:
    {resume}
    Extract structured information from the resume.
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

    Do NOT wrap in quotes or explain anything.
    """
)
    
    
    parse_chain = parse_prompt_template | llm | StrOutputParser()
    response = parse_chain.invoke({'resume' : text})
    
    
    
        
    


    try:
        # Clean Gemini output if it's wrapped in extra quotes
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # Print debug log
        # print("Gemini response:\n", cleaned)

        # Parse the JSON
        data = json.loads(cleaned)
        
        email_address = user_email
    
        # metadata = {
        #     "email" : email_address,
        #     'skills': data.get("skills", []),
        #     "projects": data.get("projects", []),
        #     "experience": data.get("experience", [])
        # }
        # vectorstore.add_texts(
        #     texts=[text],
        #     metadatas=[metadata],
        #     ids=[email_address]
        # )
        
        print(data.get("skills",[]))
        return {
            "email": email_address,
            "skills": data.get("skills", []),
            "experience": data.get("experience", []),
            "projects": data.get("projects", [])
        }

    except Exception as e:
        print("Error parsing Gemini response:", e)
        print("Raw Gemini response:\n", response)
        return {
            "error": str(e),
            "raw_gemini_output": response
        }
        
    
        
    
    