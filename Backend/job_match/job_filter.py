import json
from pymongo.mongo_client import MongoClient
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from google import genai
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = GoogleGenerativeAI(model="gemini-2.0-flash")

# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# chat = client.chats.create(model="gemini-2.0-flash")

collection = MongoClient("mongodb://localhost:27017")
db = collection['internshipmap']
resumes = db['resumes']
jobs = db['jobs']




headers = {
	"x-rapidapi-key": os.getenv("RAPID_API_KEY"),
	"x-rapidapi-host": os.getenv("RAPID_API_HOST")
}

def summarize_description(description):
    summary_prompt_template = ChatPromptTemplate.from_template(
        """
        You are given a job description:
        {description}
        
        Summarize the description to 2-3 sentences that includes 
        key skills and requirements of the job that would help an llm determine whether the job is a good fit for a user's resume.
        """)
    
    chain =  summary_prompt_template | llm | StrOutputParser()
    response = chain.invoke({'description' : description})
    # prompt = (
    #     f"Given this description of a job {description}. "
    #     "Summarize it to only innclude key skills and aspects of the job that would help determine "
    #     "If it matches witha resume. Keep it to 2-3 sentences,"
    #     )
    
    # response = chat.send_message(prompt)
    return response.text
            

def job_match(email):
    user_resume = resumes.find_one({"email" : email})
    if not user_resume:
        return {
            "error": f"No resume found for {email}"
        }
    skills = user_resume['skills']
    advanced_query = "("
    for skill in skills:
        advanced_query = advanced_query + " '" +skill + "' |"
    advanced_query = advanced_query[:-1]
    advanced_query = advanced_query + ")"
    params = {
		"offset" : "0",
		"limit" : "10",
		"location_filter" : "United States",
		"description_type" : "text",
		"type_filter" : "INTERN",
		"date_filter" : datetime.now() - timedelta(days=15),
		"advanced_title_filter" : advanced_query
	}
    job_results = requests.get("https://linkedin-job-search-api.p.rapidapi.com/active-jb-7d", headers=headers, params=params).json()
    print(job_results)
    ranked_job = []
    for i in range(10):
        job = job_results[i]
        summarized = summarize_description(job['description_text'])
        rank = {
            'title' : job['title'],
            'organization' : job['organization'],
            'date_posted' : job['date_posted'],
            'location' : job['locations_derived'],
            'type' : job['employment_type'],
            'url' : job['url'],
            'source' : job['source'],
            'description' : summarized
        }
        # print("title" + rank['title'])
        ranked_job.append(rank)
    
    resume_prompt_template = ChatPromptTemplate(
        """Given this parse resume:
        {resume}
        And this list of jobs:
        {ranked_job}
        
        Return the list of jobs, ranked from best to worst bassed of the parse resume.
        Add a 'fit' field to each job object, representing the percentage that the job matches the resume.
        Add a 'why' field, detailing why the job is and isn't a fit for the resume.
        Add an 'improvement' field, detailing what the user need to imporve or add to their resume to better fit the job.
        Only return a JSON"""
    )
    
    chain = resume_prompt_template | llm | StrOutputParser()
    response = chain.invoke({'resume' : user_resume, 'ranked_job' : ranked_job})
    # prompt = (
    # f"You are given a parsed resume:\n{user_resume}\n\n"
    # f"and a list of job postings:\n{ranked_job}\n\n"
    # "Return the list of jobs, ranked from best match to worst, based on the resume content. "
    # "Add a 'fit' field to each job, representing the match percentage as an integer (e.g., 87). "
    # "Add a 'why' field to each job, which details why you think it is a good job for the person based off the resume. "
    # "Add a 'improvement' field to each job, which details what the user can do or add to improve their resume for the job. "
    # "Respond ONLY with a valid JSON array of jobs, each including the new 'fit', 'why', and 'improvement' fields."
    # )
    
    # response = chat.send_message(prompt)
    
    try:
        
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        # print("Gemini response:\n", cleaned)
        # with open("gemini_raw_response.txt", "w", encoding="utf-8") as f:
        #     f.write(cleaned)
        
        data = json.loads(cleaned)
        print("Parsed data:", data)
        print("Type:", type(data))
        
        for i in range(10):
            temp = data[i]
            temp['description'] = job[i]['description_text']
        
        ret = {
            "email" : email,
            "jobs" : data,
            "date_accessed" : datetime.now()
        }
        
        jobs.insert_one(ret)
        return data
    except Exception as e:
        print("Error parsing Gemini response:", e)
        print("Raw Gemini response:\n", response)
        return {
            "error": str(e),
            "raw_gemini_output": response
        }