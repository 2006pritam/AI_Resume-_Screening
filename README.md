# AI Resume Screening & Candidate Clustering

An intelligent, machine-learning-powered resume screening and candidate ranking system built with **FastAPI** (Backend) and **Streamlit** (Frontend).

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
├── Dockerfile                      # Docker container definition for Render
├── render.yaml                     # Render Blueprint configuration
├── app.py                          # Root Streamlit entrypoint
├── streamlit_app.py                # Streamlit Community Cloud entrypoint
├── requirements.txt                # Streamlit dependencies
├── README.md                       # Project documentation
└── ai-resume-screener/
    ├── main.py                     # FastAPI server entrypoint
    ├── requirements.txt            # Backend ML dependencies
    ├── backend/                    # FastAPI endpoints, services, models
    ├── deployment/                 # ML models, vector indices, pre-computed data
    └── streamlit/
        ├── app.py                  # Streamlit application UI and logic
        └── requirements.txt        # Streamlit requirements
```

---

## 🌐 Cloud Deployment Architecture

| Component | Platform | URL / Configuration |
| :--- | :--- | :--- |
| **Backend API** | [Render](https://render.com/) | `https://ai-resume-screening-ik9s.onrender.com` |
| **Frontend UI** | [Streamlit Cloud](https://share.streamlit.io/) | Python app (`streamlit_app.py`) |

### 1. Backend Service on Render

Your live backend service is hosted at:
```text
https://ai-resume-screening-ik9s.onrender.com
```

### 2. Frontend on Streamlit Community Cloud

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Click **Create app**.
3. Configure your app:
   - **Repository:** `2006pritam/AI_Resume-_Screening`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
4. Under **Advanced settings** > **Secrets**, set:
   ```toml
   FASTAPI_URL = "https://ai-resume-screening-ik9s.onrender.com"
   ```
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

In a separate terminal from repository root:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
