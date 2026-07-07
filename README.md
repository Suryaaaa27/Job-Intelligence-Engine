# 🚀 Job Intelligence Engine

<p align="center">

AI-Powered Job Discovery, Intelligence & Application Automation Platform

</p>

---

# 📌 Overview

Job Intelligence Engine is an end-to-end AI-powered platform that automates the complete job application lifecycle.

Instead of manually searching for jobs, reading lengthy job descriptions, tailoring resumes, finding recruiters, and tracking applications, the system intelligently performs these tasks through a modular AI pipeline.

The project is designed using scalable software engineering principles and is being developed collaboratively by a structured engineering team.

---

# 🎯 Vision

Build an intelligent platform capable of:

- Discovering jobs from multiple sources
- Cleaning and structuring raw job data
- Understanding job descriptions using AI
- Optimizing resumes for ATS systems
- Automating recruiter outreach
- Tracking job applications
- Reducing manual effort throughout the hiring process

---

# 🏗️ Project Architecture

```
                        Job Sources
      ┌─────────────────────────────────────┐
      │ Hays │ Greenhouse │ LinkedIn │ Indeed │
      └─────────────────────────────────────┘
                      │
                      ▼
             Unified Scraper Engine
                      │
                      ▼
          Cleaning & Preprocessing Pipeline
                      │
                      ▼
        Role Classification & Taxonomy Engine
                      │
                      ▼
           Structured Job Database (SQLite)
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
 Job Description Intelligence    Resume Engine
        │                           │
        ▼                           ▼
 Skill Extraction            ATS Optimization
        │                           │
        └─────────────┬─────────────┘
                      ▼
             Outreach Automation
                      │
                      ▼
            Application Tracking
```

---

# ✅ Completed Modules (Sprint 1)

## Team A – Data Intelligence

### ✔ Scraper Framework

- Unified Scraper Architecture
- Base Scraper
- Hays Integration
- Greenhouse Integration
- LinkedIn Integration
- Indeed Integration

---

### ✔ Data Processing

- HTML Cleaning
- Data Normalization
- Salary Extraction
- Job Type Detection
- Location Standardization
- Date Standardization

---

### ✔ Advanced Deduplication

- URL Matching
- Company Matching
- SequenceMatcher Similarity
- Jaccard Similarity
- Duplicate Filtering

---

### ✔ Storage Layer

- SQLite Migration
- Repository Pattern
- CRUD Operations
- Search APIs
- Statistics APIs

---

### ✔ Classification Engine

- Taxonomy Based Classification
- Weighted Scoring
- Positive Keywords
- Negative Keywords
- Title Similarity

---

### ✔ FastAPI Backend

- Job APIs
- Search APIs
- Statistics APIs
- Pipeline Execution APIs

---

# 🚧 Current Development

## Team B – AI Intelligence

Currently under development:

- Job Description Parser
- Requirement Extraction
- Skill Extraction
- Experience Extraction
- Resume Generator
- ATS Optimization Engine
- Recruiter Outreach
- Email Automation
- Application Tracker

---

# 🛠 Technology Stack

### Backend

- Python
- FastAPI
- SQLite
- Playwright
- Requests
- BeautifulSoup

### AI / ML

- OpenAI API
- Google Gemini API
- FAISS
- Sentence Transformers
- Scikit-learn

### Frontend (Upcoming)

- React
- TailwindCSS

### Dev Tools

- Git
- GitHub
- GitHub Projects
- GitHub Issues

---

# 📂 Project Structure

```
analysis/
config/
data/
filtering/
models/
pipeline/
preprocessing/
schemas/
scraper/
search/
services/
storage/
taxonomy/
tests/
utils/
```

---

# 👥 Team Structure

## Project Lead

**Surya Srivastava**

Responsible for:

- System Architecture
- Technical Decisions
- Code Reviews
- Git Workflow
- Team Coordination

---

## Team A – Data Intelligence ✅

### Developer A - Surya Kumar Srivastava

- Multi-platform Scrapers

### Developer B - Gauri Khatokar

- Data Cleaning
- Preprocessing

### Developer C - Pratham Singh Shaurya

- Classification
- Storage
- FastAPI

**Status: Completed ✅**

---

## Team B – AI Intelligence 🚧

### Developer D - Manasvi Vaity & Koushick Mondal

- Job Description Intelligence

### Developer E - Ashmit Pradhan & Soham 

- Resume & ATS Optimization

### Developer F - Anand Raj & Pragyan

- Outreach Automation

**Status: In Progress 🚀**

---

# 📈 Roadmap

## ✅ Sprint 1

- Scraper Framework
- Data Pipeline
- SQLite
- Classification
- FastAPI

---

## 🚧 Sprint 2

- JD Intelligence
- Requirement Extraction
- Skills Extraction

---

## 📅 Sprint 3

- Resume Generator
- ATS Optimization

---

## 📅 Sprint 4

- Recruiter Finder
- Email Automation

---

## 📅 Sprint 5

- Frontend Dashboard
- Analytics
- Deployment

---

# 🚀 Git Workflow

```
Feature Branch
      │
      ▼
Pull Request
      │
      ▼
Code Review
      │
      ▼
Develop Branch
      │
      ▼
Main Branch
```

---

# 🤝 Contributing

Every contribution follows:

- Feature Branch
- Pull Request
- Code Review
- Testing
- Merge into Develop

Direct commits to `main` are not allowed.

---

# 📜 License

This project is currently under active development.

---

# ⭐ Project Status

## Sprint 1 Completed ✅

Current Phase:

**Team B – AI Intelligence Development**

---

<p align="center">

Made with ❤️ by Team Job Intelligence Engine

</p>
