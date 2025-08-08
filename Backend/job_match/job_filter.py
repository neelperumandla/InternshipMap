import json
from pymongo.mongo_client import MongoClient
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain.agents import initialize_agent, AgentType

load_dotenv()

# === Setup LLM and Embeddings === #
llm = GoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
embedding = OllamaEmbeddings(model="llama3")
vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embedding)
retriever = vectorstore.as_retriever()

# === Database === #
collection = MongoClient("mongodb://localhost:27017")
db = collection['internshipmap']
resumes = db['resumes']
jobs = db['jobs']

# === API Headers === #
headers = {
    "x-rapidapi-key": os.getenv("RAPID_API_KEY"),
    "x-rapidapi-host": os.getenv("RAPID_API_HOST")
}

# === Chain to summarize job descriptions === #
summarize_prompt = ChatPromptTemplate.from_template(
    """
    You are given a job description:
    {description}
    Summarize it to 2-3 sentences with key skills and requirements.
    """
)
summarize_chain = summarize_prompt | llm | StrOutputParser()

# === Chain to rank jobs against resume === #
ranking_prompt = ChatPromptTemplate.from_template(
    """
    Given this parsed resume:
    {resume}
    And this list of jobs:
    {ranked_job}
    Return a JSON list of jobs ranked from best to worst with 'fit', 'why', and 'improvement' fields.
    """
)
ranking_chain = ranking_prompt | llm | StrOutputParser()

# === Main Function === #
def job_match(email):
    user_resume = resumes.find_one({"email": email})
    if not user_resume:
        return {"error": f"No resume found for {email}"}

    skills = user_resume.get("skills", [])
    advanced_query = "(" + " |".join(f" '{skill}'" for skill in skills) + ")"
    
    params = {
        "offset": "0",
        "limit": "10",
        "location_filter": "United States",
        "description_type": "text",
        "type_filter": "INTERN",
        "date_filter": datetime.now() - timedelta(days=15),
        "advanced_title_filter": advanced_query
    }
    job_results = requests.get("https://linkedin-job-search-api.p.rapidapi.com/active-jb-7d", headers=headers, params=params).json()

    def summarize_job(job):
        return {
            "title": job["title"],
            "organization": job["organization"],
            "date_posted": job["date_posted"],
            "location": job["locations_derived"],
            "type": job["employment_type"],
            "url": job["url"],
            "source": job["source"],
            "description": summarize_chain.invoke({"description": job["description_text"]})
        }

    # === RunnableParallel for job summarization === #
    summarize_jobs_chain = RunnableParallel(**{
        str(i): RunnableLambda(lambda j=job_results[i]: summarize_job(j))
        for i in range(len(job_results))
    })

    ranked_job = list(summarize_jobs_chain.invoke({}).values())

    # === Run ranking chain === #
    response = ranking_chain.invoke({"resume": user_resume, "ranked_job": ranked_job})

    try:
        cleaned = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(cleaned)

        # Store jobs in MongoDB
        jobs.insert_one({
            "email": email,
            "jobs": data,
            "date_accessed": datetime.now()
        })

        return data

    except Exception as e:
        return {
            "error": str(e),
            "raw_response": response
        }