# AI Resume Screening & Candidate Clustering

An intelligent, machine-learning-powered resume screening and candidate ranking system built with **FastAPI** and **Streamlit**.

---

## 🚀 Features

- **Semantic Matching**: Evaluates conceptual relevance between resumes and job descriptions using embedding representations.
- **Skill Extraction & Matching**: Automatically parses candidate skills and compares against required and preferred qualifications.
- **Experience Scoring**: Calculates and verifies candidate work experience from employment dates and textual descriptions.
- **Candidate Clustering & Similarity Search**: Uses FAISS vector search and KMeans clustering to identify similar profiles.
- **Interactive UI**: Clean and intuitive Streamlit dashboard for both single resume analysis and batch processing.

---

## 📁 Repository Structure

```text
├── app.py                          # Root Streamlit entrypoint
├── streamlit_app.py                # Streamlit Community Cloud entrypoint
├── requirements.txt                # Streamlit dependencies
├── README.md                       # Project documentation
└── ai-resume-screener/
    ├── main.py                     # FastAPI server entrypoint
    ├── requirements.txt            # Backend dependencies
    ├── vercel.json                 # Vercel deployment configuration
    ├── backend/                    # FastAPI endpoints, services, models
    ├── deployment/                 # ML models, vector indices, pre-computed data
    └── streamlit/
        ├── app.py                  # Streamlit application UI and logic
        └── requirements.txt        # Streamlit requirements
```

---

## 🌐 Deploy to Streamlit Community Cloud

1. Log in to [Streamlit Community Cloud](https://share.streamlit.io/) with your GitHub account.
2. Click **Create app** (or **New app**).
3. Configure your app settings:
   - **Repository:** `2006pritam/AI_Resume-_Screening`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py` (or `app.py`)
4. *(Optional)* In the sidebar of the deployed application, enter your deployed FastAPI URL if your backend is hosted online (e.g. on Vercel or Render).
5. Click **Deploy!**.

---

## 💻 Local Setup & Development

### 1. Run the FastAPI Backend

```bash
cd ai-resume-screener
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Run the Streamlit Frontend

In a separate terminal from the repository root:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
