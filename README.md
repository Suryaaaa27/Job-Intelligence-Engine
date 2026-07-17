# 🚀 Job Intelligence Engine

<p align="center">

### AI-Powered Job Discovery, Intelligence & Recruitment Automation Platform

**Discover • Analyze • Match • Apply**

</p>

---

# 📌 Overview

**Job Intelligence Engine** is an AI-powered platform that automates the entire job discovery and analysis pipeline.

Instead of manually searching job portals, reading lengthy job descriptions, extracting skills, identifying recruiters, and tailoring resumes, the platform intelligently performs these tasks through a modular, scalable architecture.

The system combines **web scraping, AI-powered job intelligence, data engineering, and recruiter enrichment** into a unified pipeline designed to simplify and accelerate the hiring process.

---

# 🎯 Vision

Our goal is to build an intelligent platform capable of:

- 🌍 Discovering jobs from multiple job portals
- 🧹 Cleaning and normalizing raw job data
- 🧠 Understanding job descriptions using AI
- 📊 Extracting skills, responsibilities and requirements
- 👤 Identifying recruiters from job postings
- 📄 Optimizing resumes for ATS systems
- 📧 Automating recruiter outreach
- 📈 Tracking job applications and analytics

---

# 🏗️ Project Architecture

```text
                     Job Sources
 ┌────────────────────────────────────────────┐
 │ Hays │ Greenhouse │ LinkedIn │ Indeed │
 └────────────────────────────────────────────┘
                     │
                     ▼
            Unified Scraper Engine
                     │
                     ▼
         Cleaning & Normalization Pipeline
                     │
                     ▼
      Job Detail & Intelligence Extraction
                     │
                     ▼
      AI-powered JD Intelligence Analyzer
                     │
                     ▼
         MongoDB Unified Job Repository
                     │
      ┌──────────────┴──────────────┐
      ▼                             ▼
 Resume Intelligence          Recruiter Intelligence
      │                             │
      ▼                             ▼
 ATS Optimization           Outreach Automation
      │                             │
      └──────────────┬──────────────┘
                     ▼
            Application Tracker
```

---

# ✅ Current Features

## 🌐 Multi-platform Job Scraping

Supported platforms:

- ✅ Hays
- ✅ Greenhouse
- ✅ LinkedIn
- ✅ Indeed

### Hays Highlights

- API-driven scraping
- Cursor-based pagination
- High-speed data collection
- Raw API response archival
- Duplicate detection
- Recruiter extraction directly from API
- Unified Job model generation

---

## 🧹 Data Processing Pipeline

- HTML Cleaning
- Text Normalization
- Salary Standardization
- Employment Type Detection
- Workplace Type Detection
- Date Parsing
- Location Normalization

---

## 🧠 Job Intelligence Engine

Automatically extracts:

- Skills
- Responsibilities
- Education
- Experience
- Benefits
- ATS Keywords
- Required Skills
- Preferred Skills
- Seniority
- Completeness Score

---

## 👤 Recruiter Intelligence

Automatically extracts:

- Recruiter Name
- Recruiter Email

without opening individual job pages.

---

## 📦 Storage Layer

- MongoDB Repository
- Repository Pattern
- Duplicate Detection
- CRUD Operations
- Incremental Updates

---

## 🔍 Classification Engine

- Taxonomy-based Classification
- Weighted Scoring
- Positive & Negative Keyword Matching
- Similarity Matching

---

## ⚙️ FastAPI Backend

REST APIs for:

- Job Search
- Job Retrieval
- Statistics
- Pipeline Execution

---

# 🛠 Technology Stack

## Backend

- Python
- FastAPI
- MongoDB
- Playwright
- Requests
- BeautifulSoup

## AI / ML

- OpenAI
- Google Gemini
- Sentence Transformers
- FAISS
- Scikit-learn

## Data

- MongoDB
- JSON
- Pandas

## Dev Tools

- Git
- GitHub
- GitHub Projects
- GitHub Issues

---

# 📂 Project Structure

```text
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

# 🚀 Current Pipeline

```text
Job Search
      │
      ▼
Multi-platform Scrapers
      │
      ▼
Raw API Data
      │
      ▼
Cleaner & Preprocessing
      │
      ▼
Job Detail Extraction
      │
      ▼
JD Intelligence Analyzer
      │
      ▼
Recruiter Intelligence
      │
      ▼
MongoDB Repository
      │
      ▼
Search APIs
```

---

# 👥 Team Structure

## Project Lead

### **Surya Kumar Srivastava**

Responsible for:

- System Architecture
- AI Pipeline Design
- Scraper Development
- Technical Decisions
- Code Reviews
- Git Workflow
- Team Coordination

---

## Team A – Data Intelligence ✅

### Surya Kumar Srivastava

- Multi-platform Scrapers
- Hays API Integration
- Data Engineering

### Gauri Khatokar

- Data Cleaning
- Preprocessing

### Pratham Singh Shaurya

- Classification
- Storage
- FastAPI Backend

---

## Team B – AI Intelligence 🚧

### Manasvi Vaity & Koushick Mondal

- Job Description Intelligence
- Information Extraction

### Ashmit Pradhan & Soham

- Resume Intelligence
- ATS Optimization

### Anand Raj & Pragyan

- Recruiter Outreach
- Email Automation

---

# 📈 Roadmap

## ✅ Completed

- Multi-platform Scraper Framework
- Hays API Integration
- Greenhouse Integration
- LinkedIn Integration
- Indeed Integration
- Data Cleaning Pipeline
- Job Detail Extraction
- JD Intelligence Analyzer
- Recruiter Intelligence
- MongoDB Storage Layer
- Classification Engine
- FastAPI Backend

---

## 🚧 In Progress

- Resume Matching Engine
- ATS Resume Optimization
- Recruiter Outreach Automation
- Email Generation
- Application Tracker

---

## 🔜 Upcoming

- Resume Generator
- Frontend Dashboard
- Analytics
- AI Career Assistant
- Deployment

---

# 🔄 Git Workflow

```text
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
- Merge into `develop`

Direct commits to `main` are not allowed.

---

# 📜 License

This project is currently under active development.

---

# 📊 Current Project Status

| Module | Status |
|---------|--------|
| Multi-platform Scrapers | ✅ Completed |
| Data Processing Pipeline | ✅ Completed |
| Job Intelligence Engine | ✅ Completed |
| Recruiter Intelligence | ✅ Completed |
| MongoDB Storage | ✅ Completed |
| Classification Engine | ✅ Completed |
| FastAPI Backend | ✅ Completed |
| Resume Intelligence | 🚧 In Progress |
| ATS Optimization | 🚧 In Progress |
| Recruiter Outreach | 🚧 In Progress |
| Frontend Dashboard | 📅 Planned |

---

<p align="center">

### ⭐ Built with ❤️ by Team Job Intelligence Engine ⭐

</p>
