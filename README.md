# AI RAG-based Job Matcher

A microservices-driven AI platform that parses resumes, ranks jobs, and provides personalized recommendations for job seekers.

Overview

The AI RAG-based Job Matcher leverages state-of-the-art AI techniques and microservices architecture to provide tailored job recommendations. It processes user resumes, ingests job listings, ranks opportunities, and generates actionable feedback to help candidates improve their fit and increase their chances of success.

Key Features

Resume Parsing: Automatically extracts relevant skills, experience, and qualifications from resumes.

Job Ingestion: Collects and normalizes job postings from multiple sources.

AI-driven Job Ranking: Uses a Retrieval-Augmented Generation (RAG) pipeline with Chroma to generate ordered job recommendations and fit scores.

Personalized Feedback: Suggests actionable improvements to enhance candidate profiles.

Microservices Architecture: Independent services for resume parsing, job ingestion, ranking, and feedback, enabling scalability and modular development.

LLM Integration: Utilizes Gemini and Ollama LLMs for advanced language understanding and recommendation generation.

Tech Stack

Frontend: React

Backend: Flask, FastAPI

Database: MongoDB

AI / LLMs: LangChain, Gemini, Ollama

Vector Database: Chroma (for RAG pipeline)

Architecture

Microservices: Resume Parser, Job Ingestion, Job Ranking, Feedback Generator

RAG Pipeline: Chroma database stores job embeddings, LangChain handles retrieval, Gemini and Ollama generate insights.

Integration: Services communicate via REST APIs, allowing independent scaling and updates.
