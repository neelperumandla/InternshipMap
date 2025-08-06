import json
from pymongo.mongo_client import MongoClient
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from google import genai
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chat = client.chats.create(model="gemini-2.0-flash")

collection = MongoClient("mongodb://localhost:27017")
db = collection['internshipmap']
resumes = db['resumes']
jobs = db['jobs']




headers = {
	"x-rapidapi-key": os.getenv("RAPID_API_KEY"),
	"x-rapidapi-host": os.getenv("RAPID_API_HOST")
}

def summarize_description(description):
    prompt = (
        f"Given this description of a job {description}. "
        "Summarize it to only innclude key skills and aspects of the job that would help determine "
        "If it matches witha resume. Keep it to 2-3 sentences,"
        )
    
    response = chat.send_message(prompt)
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
		"limit" : "5",
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
        rank = {
            'title' : job['title'],
            'organization' : job['organization'],
            'date_posted' : job['date_posted'],
            'location' : job['locations_derived'],
            'type' : job['employment_type'],
            'url' : job['url'],
            'source' : job['source'],
            'description' : summarize_description[job['description_text']]
        }
        # print("title" + rank['title'])
        ranked_job.append(rank)
    
    
    prompt = (
    f"You are given a parsed resume:\n{user_resume}\n\n"
    f"and a list of job postings:\n{ranked_job}\n\n"
    "Return the list of jobs, ranked from best match to worst, based on the resume content. "
    "Add a 'fit' field to each job, representing the match percentage as an integer (e.g., 87). "
    "Add a 'why' field to each job, which details why you think it is a good job for the person based off the resume. "
    "Add a 'improvement' field to each job, which details what the user can do or add to improve their resume for the job. "
    "Respond ONLY with a valid JSON array of jobs, each including the new 'fit', 'why', and 'improvement' fields."
    )
    
    response = chat.send_message(prompt)
    
    try:
        
        cleaned = response.text.strip()
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
            temp['description'] = job['description_text']
        
        ret = {
            "email" : email,
            "jobs" : data,
            "date_accessed" : datetime.now()
        }
        
        jobs.insert_one(ret)
        return data
    except Exception as e:
        print("Error parsing Gemini response:", e)
        print("Raw Gemini response:\n", response.text)
        return {
            "error": str(e),
            "raw_gemini_output": response.text
        }