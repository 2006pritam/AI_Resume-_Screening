"""AI Resume Screener - Streamlit dashboard UI on top of the FastAPI screening API."""

from __future__ import annotations

import os
import random

import altair as alt
import pandas as pd
import requests
import streamlit as st

DEFAULT_API_URL = "https://ai-resume-screening-ik9s.onrender.com"

NAV_ITEMS = [
    ("Dashboard", "🏠"),
    ("Screen Resumes", "📄"),
    ("Jobs", "💼"),
    ("Candidates", "👥"),
    ("Clusters", "🧩"),
    ("Analytics", "📊"),
]

CLUSTER_COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EF4444"]

DEFAULT_JOBS = [
    {
        "title": "Software Engineer (React)",
        "description": (
            "We are hiring a Software Engineer to build modern web interfaces.\n\n"
            "Requirements:\n"
            "- 3+ years of professional experience with React and JavaScript\n"
            "- Strong knowledge of TypeScript, HTML and CSS\n"
            "- Experience with Node.js REST APIs\n"
            "- Familiarity with Git, testing and CI/CD\n"
            "- Bachelor's degree in Computer Science or equivalent experience"
        ),
    },
    {
        "title": "Graphic Designer",
        "description": (
            "We are looking for a Graphic Designer to produce visual assets.\n\n"
            "Requirements:\n"
            "- 2+ years of design experience\n"
            "- Proficiency in Adobe Photoshop, Illustrator and Figma\n"
            "- Strong portfolio covering branding and social media design\n"
            "- Good understanding of typography and colour theory"
        ),
    },
    {
        "title": "Data Analyst",
        "description": (
            "We are hiring a Data Analyst to turn data into decisions.\n\n"
            "Requirements:\n"
            "- 2+ years of analytics experience\n"
            "- Strong SQL and Python (pandas) skills\n"
            "- Experience building dashboards in Power BI or Tableau\n"
            "- Comfortable communicating findings to non-technical teams"
        ),
    },
]

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------
def resolve_api_url():
    """Resolve the backend URL from secrets, then environment, then the default."""
    for key in ("FASTAPI_URL", "RENDER_URL", "API_URL"):
        try:
            value = st.secrets[key]
        except Exception:
            value = None
        if value:
            return str(value).rstrip("/")

    for key in ("FASTAPI_URL", "RENDER_URL", "API_URL"):
        value = os.environ.get(key)
        if value:
            return value.rstrip("/")

    return DEFAULT_API_URL


# --------------------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg: #F4F7FB;
    --card: #FFFFFF;
    --border: #E6EBF2;
    --text: #0F172A;
    --muted: #64748B;
    --blue: #2563EB;
    --purple: #7C5CFC;
    --green: #16A34A;
    --amber: #D97706;
}

html, body, .stApp, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.stApp, [data-testid="stAppViewContainer"] { background: var(--bg); }
[data-testid="stHeader"] { background: transparent; height: 0; }
[data-testid="stToolbar"] { right: 8px; }
footer, #MainMenu { visibility: hidden; }

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* ---------------- sidebar ---------------- */
section[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] > div { padding-top: 1.1rem; }

.brand { display: flex; align-items: center; gap: 10px; padding: 2px 4px 18px 4px; }
.brand-logo {
    width: 34px; height: 34px; border-radius: 9px;
    background: linear-gradient(135deg, #3B82F6, #2563EB);
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-size: 17px; font-weight: 700;
}
.brand-name { font-size: 16px; font-weight: 700; color: var(--text); letter-spacing: -0.2px; }

.nav-label {
    font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: #94A3B8;
    padding: 6px 6px 8px 6px;
}

/* nav buttons: secondary = idle, primary = active */
section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    width: 100%;
    justify-content: flex-start;
    text-align: left;
    border: none;
    border-radius: 9px;
    padding: 0.55rem 0.7rem;
    font-size: 14px;
    font-weight: 500;
    box-shadow: none;
    margin-bottom: 2px;
}
section[data-testid="stSidebar"] button[kind="secondary"],
section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
    background: transparent;
    color: #475569;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover,
section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
    background: #F1F5F9;
    color: var(--text);
}
section[data-testid="stSidebar"] button[kind="primary"],
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background: #EAF1FE !important;
    color: var(--blue) !important;
    font-weight: 600 !important;
}

.side-note {
    margin-top: 18px; padding: 12px 13px;
    background: #F8FAFC; border: 1px solid var(--border);
    border-radius: 10px; font-size: 12px; color: var(--muted); line-height: 1.6;
}
.side-note b { color: var(--text); }

/* ---------------- top header ---------------- */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    background: #FFFFFF; border: 1px solid var(--border); border-radius: 14px;
    padding: 12px 18px; margin-bottom: 18px;
}
.topbar-title { font-size: 15px; font-weight: 600; color: var(--text); }
.topbar-right { display: flex; align-items: center; gap: 14px; }
.api-badge {
    display: inline-flex; align-items: center; gap: 7px;
    font-size: 13px; font-weight: 500; color: #334155;
}
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.dot-on { background: #22C55E; box-shadow: 0 0 0 3px rgba(34,197,94,.18); }
.dot-off { background: #EF4444; box-shadow: 0 0 0 3px rgba(239,68,68,.18); }
.avatar {
    width: 34px; height: 34px; border-radius: 50%;
    background: linear-gradient(135deg, #8B5CF6, #7C3AED);
    color: #fff; font-size: 14px; font-weight: 600;
    display: flex; align-items: center; justify-content: center;
}

/* ---------------- hero ---------------- */
.hero {
    display: flex; align-items: center; justify-content: space-between; gap: 30px;
    background: #FFFFFF; border: 1px solid var(--border); border-radius: 16px;
    padding: 30px 34px; margin-bottom: 20px;
}
.hero h1 {
    font-size: 30px; font-weight: 700; color: var(--text);
    margin: 0 0 10px 0; letter-spacing: -0.5px; line-height: 1.25;
}
.hero p { font-size: 14.5px; color: var(--muted); margin: 0; max-width: 520px; line-height: 1.65; }

.illus { position: relative; width: 210px; height: 140px; flex: 0 0 auto; }
.illus-doc {
    position: absolute; left: 24px; top: 10px; width: 118px; height: 120px;
    background: #EFF6FF; border: 1px solid #DBEAFE; border-radius: 10px; padding: 14px 13px;
}
.illus-line { height: 7px; border-radius: 4px; background: #BFDBFE; margin-bottom: 9px; }
.illus-line.s { width: 55%; }
.illus-line.m { width: 80%; }
.illus-line.l { width: 100%; }
.illus-check {
    position: absolute; right: 22px; bottom: 16px; width: 46px; height: 46px;
    border-radius: 50%; background: #DCFCE7; border: 1px solid #BBF7D0;
    display: flex; align-items: center; justify-content: center;
    color: #16A34A; font-size: 22px; font-weight: 700;
}
.illus-blob {
    position: absolute; border-radius: 50%; background: #DBEAFE;
}
.illus-blob.b1 { width: 16px; height: 16px; right: 74px; top: 12px; }
.illus-blob.b2 { width: 10px; height: 10px; right: 34px; top: 44px; background: #C7D2FE; }
.illus-blob.b3 { width: 22px; height: 22px; left: 4px; bottom: 6px; background: #E0E7FF; }

/* ---------------- cards ---------------- */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div > [data-testid="stVerticalBlock"]) {
    background: transparent;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF;
    border: 1px solid var(--border) !important;
    border-radius: 14px;
    padding: 20px 22px;
}

.card-title { font-size: 15.5px; font-weight: 600; color: var(--text); margin: 0 0 4px 0; }
.card-sub { font-size: 12.5px; color: var(--muted); margin: 0 0 12px 0; }
.card-hint { font-size: 12px; color: #94A3B8; margin: 6px 0 0 0; }

/* file uploader as a drop zone */
[data-testid="stFileUploaderDropzone"] {
    background: #F8FAFC;
    border: 1.5px dashed #CBD5E1;
    border-radius: 12px;
    padding: 14px 16px;
}
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--blue); background: #F5F9FF; }
[data-testid="stFileUploaderDropzone"] button {
    background: var(--blue) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
}
div[data-testid="stColumn"]:nth-of-type(2) [data-testid="stFileUploaderDropzone"] button,
div[data-testid="column"]:nth-of-type(2) [data-testid="stFileUploaderDropzone"] button {
    background: var(--purple) !important;
}

/* main-area primary button = green action */
.block-container button[kind="primary"],
.block-container [data-testid="stBaseButton-primary"] {
    background: var(--green) !important;
    border: none !important;
    color: #fff !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
}
.block-container button[kind="primary"]:hover,
.block-container [data-testid="stBaseButton-primary"]:hover {
    background: #15803D !important;
}
.block-container button[kind="secondary"],
.block-container [data-testid="stBaseButton-secondary"] {
    border: 1px solid var(--border) !important;
    background: #FFFFFF !important;
    color: #334155 !important;
    border-radius: 9px !important;
    font-weight: 500 !important;
}

/* ---------------- stat cards ---------------- */
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 4px 0 20px 0; }
.stat { border-radius: 14px; padding: 18px 20px; border: 1px solid transparent; }
.stat-top { display: flex; align-items: center; justify-content: space-between; }
.stat-label { font-size: 12.5px; font-weight: 500; color: #475569; }
.stat-icon { font-size: 18px; opacity: .9; }
.stat-value { font-size: 30px; font-weight: 700; color: var(--text); margin-top: 6px; letter-spacing: -0.5px; }
.stat-foot { font-size: 11.5px; color: var(--muted); margin-top: 3px; }
.stat.blue   { background: #EFF6FF; border-color: #DBEAFE; }
.stat.green  { background: #F0FDF4; border-color: #DCFCE7; }
.stat.amber  { background: #FFFBEB; border-color: #FDE68A; }
.stat.purple { background: #F5F3FF; border-color: #EDE9FE; }

.mini-pill {
    display: inline-block; font-size: 11px; font-weight: 600;
    padding: 2px 8px; border-radius: 999px; background: #DCFCE7; color: #15803D;
}

/* ---------------- pills / table ---------------- */
.pill {
    display: inline-block; font-size: 12.5px; font-weight: 600;
    padding: 3px 11px; border-radius: 999px;
}
.pill-green { background: #DCFCE7; color: #15803D; }
.pill-amber { background: #FEF3C7; color: #B45309; }
.pill-red   { background: #FEE2E2; color: #B91C1C; }
.pill-grey  { background: #F1F5F9; color: #475569; }

.th {
    font-size: 11.5px; font-weight: 600; letter-spacing: .05em;
    text-transform: uppercase; color: #94A3B8; padding-bottom: 2px;
}
.td { font-size: 13.5px; color: #334155; padding-top: 7px; }
.td-strong { font-size: 13.5px; font-weight: 600; color: var(--text); padding-top: 7px; }
.td-muted { font-size: 12.5px; color: var(--muted); padding-top: 8px; }
.rowline { border-top: 1px solid #F1F5F9; margin: 6px 0 0 0; }

.legend { display: flex; flex-direction: column; gap: 9px; padding-top: 6px; }
.legend-row { display: flex; align-items: center; gap: 9px; font-size: 13px; color: #334155; }
.legend-swatch { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }
.legend-count { color: var(--muted); font-size: 12.5px; margin-left: auto; }

.empty {
    text-align: center; padding: 34px 18px; color: var(--muted); font-size: 13.5px;
}
.empty-icon { font-size: 30px; display: block; margin-bottom: 8px; opacity: .7; }

.skill-chip {
    display: inline-block; font-size: 12px; padding: 3px 10px; margin: 0 6px 6px 0;
    border-radius: 999px; background: #F1F5F9; color: #334155; border: 1px solid var(--border);
}
.skill-chip.ok   { background: #F0FDF4; color: #15803D; border-color: #DCFCE7; }
.skill-chip.miss { background: #FEF2F2; color: #B91C1C; border-color: #FEE2E2; }

div[data-testid="stExpander"] details {
    border: 1px solid var(--border); border-radius: 12px; background: #FFFFFF;
}
hr { border-color: #EDF2F7; }
</style>
"""


# --------------------------------------------------------------------------------------
# API layer
# --------------------------------------------------------------------------------------
def to_float(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def percentage_text(value):
    number = to_float(value)
    if number is None:
        return "N/A"
    if number <= 1:
        number *= 100
    return f"{number:.2f}%"


def to_unit_score(value):
    """Return a match score on a 0..1 scale regardless of the API's unit."""
    number = to_float(value)
    if number is None:
        return None
    if number > 1:
        number = number / 100.0
    return max(0.0, min(1.0, number))


def flatten_actual_screening(screening, filename="Resume"):
    pre_screen = screening.get("pre_screen") or {}
    skills = screening.get("skills") or {}
    experience = screening.get("experience") or {}
    model_scores = screening.get("model_scores") or {}
    candidate = screening.get("candidate") or {}

    match_score = screening.get("match_score_percent")
    if match_score is None:
        match_score = screening.get("match_score")

    return {
        "resume_filename": candidate.get("filename") or filename,
        "match_score": match_score,
        "pre_screen": pre_screen.get("status"),
        "pre_screen_ready": pre_screen.get("ready"),
        "cluster": screening.get("cluster"),
        "experience_score": model_scores.get("experience_score"),
        "candidate_experience_years": experience.get("candidate_years"),
        "candidate_experience_display": experience.get("candidate_display"),
        "required_experience_years": experience.get("required_years"),
        "required_experience_display": experience.get("required_display"),
        "matched_skills": skills.get("matched") or [],
        "missing_skills": skills.get("missing") or [],
        "education": candidate.get("education"),
        "positive_factors": screening.get("positive_factors") or [],
        "review_flags": screening.get("review_flags") or [],
        "raw": screening,
    }


def normalize_batch_response(data):
    results = []
    for item in (data or {}).get("results", []) or []:
        if not isinstance(item, dict):
            continue
        screening = item.get("screening")
        if not isinstance(screening, dict):
            continue
        filename = item.get("filename") or f"Resume {item.get('index', len(results) + 1)}"
        flat = flatten_actual_screening(screening, filename)
        flat["status"] = item.get("status")
        results.append(flat)
    return results


def normalize_single_response(data, filename):
    if not isinstance(data, dict):
        return []

    screening = data.get("screening")
    if isinstance(screening, dict):
        return [flatten_actual_screening(screening, filename)]

    if "match_score" in data or "match_score_percent" in data:
        return [flatten_actual_screening(data, filename)]

    match = data.get("match") or {}
    pre_screen = data.get("pre_screen") or {}
    skills = pre_screen.get("skills") or {}
    education = pre_screen.get("education") or {}
    cluster = data.get("cluster") or {}
    model = data.get("model") or {}
    features = model.get("features") or {}

    return [
        {
            "resume_filename": filename,
            "match_score": match.get("percentage"),
            "pre_screen": pre_screen.get("overall"),
            "pre_screen_ready": None,
            "cluster": cluster.get("cluster_id"),
            "experience_score": model.get("experience_score"),
            "candidate_experience_years": features.get("candidate_experience_years"),
            "candidate_experience_display": None,
            "required_experience_years": features.get("required_experience_years"),
            "required_experience_display": None,
            "matched_skills": skills.get("matched") or [],
            "missing_skills": skills.get("missing") or [],
            "education": education.get("matched"),
            "positive_factors": match.get("positive_factors") or [],
            "review_flags": match.get("review_flags") or [],
            "raw": data,
        }
    ]


def request_single_screen(api_url, uploaded_file, job_title, job_description, similar_top_k):
    response = requests.post(
        f"{api_url}/api/v1/screen",
        files={
            "resume": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type or "application/octet-stream",
            )
        },
        data={
            "job_description": job_description,
            "title": job_title,
            "similar_top_k": str(similar_top_k),
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json()


def request_batch_screen(api_url, uploaded_files, job_title, job_description):
    multipart_files = []
    for uploaded_file in uploaded_files:
        multipart_files.append(
            (
                "resumes",
                (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type or "application/octet-stream",
                ),
            )
        )
    response = requests.post(
        f"{api_url}/api/v1/batch-screen",
        files=multipart_files,
        data={"job_description": job_description, "title": job_title},
        timeout=600,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60, show_spinner=False)
def check_api(api_url):
    """Return True when the backend answers on any of its health endpoints."""
    for path in ("/health", "/api/v1/health", "/"):
        try:
            response = requests.get(f"{api_url}{path}", timeout=8)
            if response.status_code < 500:
                return True
        except requests.RequestException:
            continue
    return False


def run_screening(api_url, job_title, job_description, files, similar_top_k):
    """Screen one or many resumes and store the normalised results in session state."""
    if len(files) == 1:
        payload = request_single_screen(api_url, files[0], job_title, job_description, similar_top_k)
        results = normalize_single_response(payload, files[0].name)
    else:
        payload = request_batch_screen(api_url, files, job_title, job_description)
        results = normalize_batch_response(payload)

    st.session_state["screening_results"] = results
    st.session_state["raw_response"] = payload
    st.session_state["screened_job"] = job_title
    return results


# --------------------------------------------------------------------------------------
# Text extraction for job description files
# --------------------------------------------------------------------------------------
def extract_text(uploaded_file):
    """Best-effort plain text extraction from a .txt / .pdf / .docx upload."""
    if uploaded_file is None:
        return ""

    name = (uploaded_file.name or "").lower()
    data = uploaded_file.getvalue()

    if name.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        import io

        try:
            try:
                from pypdf import PdfReader
            except ImportError:
                from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(data))
            return "\n".join((page.extract_text() or "") for page in reader.pages).strip()
        except Exception:
            st.warning("Could not read that PDF. Paste the job description text instead.")
            return ""

    if name.endswith(".docx"):
        import io

        try:
            import docx2txt

            return (docx2txt.process(io.BytesIO(data)) or "").strip()
        except Exception:
            pass
        try:
            from docx import Document

            document = Document(io.BytesIO(data))
            return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
        except Exception:
            st.warning("Could not read that DOCX. Paste the job description text instead.")
            return ""

    return data.decode("utf-8", errors="ignore")


# --------------------------------------------------------------------------------------
# Derived metrics
# --------------------------------------------------------------------------------------
def candidate_name(result):
    stem = os.path.splitext(result.get("resume_filename") or "Resume")[0]
    cleaned = stem.replace("_", " ").replace("-", " ").strip()
    return cleaned.title() if cleaned else "Resume"


def experience_text(result):
    display = result.get("candidate_experience_display")
    if display:
        return str(display)
    years = to_float(result.get("candidate_experience_years"))
    if years is None:
        return "—"
    return f"{years:.0f} yrs" if years == int(years) else f"{years:.1f} yrs"


def pill_class(score):
    if score is None:
        return "pill-grey"
    if score >= 0.75:
        return "pill-green"
    if score >= 0.60:
        return "pill-amber"
    return "pill-red"


def sorted_results(results):
    return sorted(results, key=lambda r: to_unit_score(r.get("match_score")) or 0.0, reverse=True)


def compute_stats(results):
    scores = [s for s in (to_unit_score(r.get("match_score")) for r in results) if s is not None]
    clusters = {r.get("cluster") for r in results if r.get("cluster") is not None}
    return {
        "total": len(results),
        "high": sum(1 for s in scores if s > 0.75),
        "average": (sum(scores) / len(scores)) if scores else None,
        "clusters": len(clusters),
    }


def cluster_counts(results):
    counts = {}
    for result in results:
        cluster = result.get("cluster")
        if cluster is None:
            continue
        counts[str(cluster)] = counts.get(str(cluster), 0) + 1
    return dict(sorted(counts.items(), key=lambda item: str(item[0])))


# --------------------------------------------------------------------------------------
# Reusable UI blocks
# --------------------------------------------------------------------------------------
def render_topbar(page, connected):
    dot = "dot-on" if connected else "dot-off"
    label = "API Connected" if connected else "API Offline"
    st.markdown(
        f"""
        <div class="topbar">
            <div class="topbar-title">{page}</div>
            <div class="topbar-right">
                <span class="api-badge"><span class="dot {dot}"></span>{label}</span>
                <div class="avatar">A</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <div class="hero">
            <div>
                <h1>AI-Powered Resume Screening</h1>
                <p>Upload job description and resumes to get AI-powered match scores
                   and candidate clustering</p>
            </div>
            <div class="illus">
                <div class="illus-doc">
                    <div class="illus-line l"></div>
                    <div class="illus-line m"></div>
                    <div class="illus-line l"></div>
                    <div class="illus-line s"></div>
                    <div class="illus-line m"></div>
                </div>
                <div class="illus-blob b1"></div>
                <div class="illus-blob b2"></div>
                <div class="illus-blob b3"></div>
                <div class="illus-check">&#10003;</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats(stats):
    average = f"{stats['average']:.2f}" if stats["average"] is not None else "—"
    st.markdown(
        f"""
        <div class="stats">
            <div class="stat blue">
                <div class="stat-top">
                    <span class="stat-label">Total Candidates</span>
                    <span class="stat-icon">👥</span>
                </div>
                <div class="stat-value">{stats['total']}</div>
                <div class="stat-foot">resumes screened</div>
            </div>
            <div class="stat green">
                <div class="stat-top">
                    <span class="stat-label">High Matches</span>
                    <span class="stat-icon">🏆</span>
                </div>
                <div class="stat-value">{stats['high']} <span class="mini-pill">&gt; 0.75</span></div>
                <div class="stat-foot">strong fit for the role</div>
            </div>
            <div class="stat amber">
                <div class="stat-top">
                    <span class="stat-label">Avg Match Score</span>
                    <span class="stat-icon">📊</span>
                </div>
                <div class="stat-value">{average}</div>
                <div class="stat-foot">across all candidates</div>
            </div>
            <div class="stat purple">
                <div class="stat-top">
                    <span class="stat-label">Formed Clusters</span>
                    <span class="stat-icon">🧩</span>
                </div>
                <div class="stat-value">{stats['clusters']}</div>
                <div class="stat-foot">candidate groups</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty(icon, message):
    st.markdown(
        f'<div class="empty"><span class="empty-icon">{icon}</span>{message}</div>',
        unsafe_allow_html=True,
    )


def render_candidate_table(results, limit=None, key_prefix="row"):
    rows = sorted_results(results)
    if limit:
        rows = rows[:limit]

    header = st.columns([0.5, 2.4, 1.5, 1.4, 3.2, 1.2])
    for column, title in zip(
        header, ["#", "Name", "Match Score", "Experience", "Key Skills", "Actions"]
    ):
        column.markdown(f'<div class="th">{title}</div>', unsafe_allow_html=True)
    st.markdown('<div class="rowline"></div>', unsafe_allow_html=True)

    for index, result in enumerate(rows, start=1):
        score = to_unit_score(result.get("match_score"))
        score_text = f"{score:.2f}" if score is not None else "N/A"
        skills = result.get("matched_skills") or []
        skills_text = ", ".join(str(skill) for skill in skills[:3]) or "—"

        cols = st.columns([0.5, 2.4, 1.5, 1.4, 3.2, 1.2])
        cols[0].markdown(f'<div class="td-muted">{index}</div>', unsafe_allow_html=True)
        cols[1].markdown(
            f'<div class="td-strong">{candidate_name(result)}</div>', unsafe_allow_html=True
        )
        cols[2].markdown(
            f'<div class="td"><span class="pill {pill_class(score)}">{score_text}</span></div>',
            unsafe_allow_html=True,
        )
        cols[3].markdown(f'<div class="td">{experience_text(result)}</div>', unsafe_allow_html=True)
        cols[4].markdown(f'<div class="td">{skills_text}</div>', unsafe_allow_html=True)
        with cols[5]:
            if st.button("View", key=f"{key_prefix}_{index}", use_container_width=True):
                st.session_state["selected_candidate"] = result.get("resume_filename")
                st.session_state["page"] = "Candidates"
                st.rerun()
        st.markdown('<div class="rowline"></div>', unsafe_allow_html=True)


def cluster_chart(counts):
    """Layered Altair scatter: soft blobs behind deterministic candidate points."""
    centers = [(0.26, 0.72), (0.63, 0.80), (0.46, 0.38), (0.80, 0.50), (0.20, 0.24)]
    rng = random.Random(7)

    blobs, points = [], []
    for index, (cluster, count) in enumerate(counts.items()):
        cx, cy = centers[index % len(centers)]
        label = f"Cluster {cluster}"
        blobs.append({"x": cx, "y": cy, "cluster": label, "size": 9000 + count * 220})
        for _ in range(min(int(count), 16)):
            points.append(
                {
                    "x": min(max(cx + rng.uniform(-0.09, 0.09), 0.03), 0.97),
                    "y": min(max(cy + rng.uniform(-0.09, 0.09), 0.03), 0.97),
                    "cluster": label,
                }
            )

    labels = [f"Cluster {cluster}" for cluster in counts]
    scale = alt.Scale(domain=labels, range=CLUSTER_COLORS[: len(labels)] or CLUSTER_COLORS)
    axis = alt.Axis(labels=False, ticks=False, domain=False, grid=False, title=None)

    blob_layer = (
        alt.Chart(pd.DataFrame(blobs))
        .mark_circle(opacity=0.13)
        .encode(
            x=alt.X("x:Q", scale=alt.Scale(domain=[0, 1]), axis=axis),
            y=alt.Y("y:Q", scale=alt.Scale(domain=[0, 1]), axis=axis),
            size=alt.Size("size:Q", scale=alt.Scale(range=[5000, 22000]), legend=None),
            color=alt.Color("cluster:N", scale=scale, legend=None),
        )
    )
    point_layer = (
        alt.Chart(pd.DataFrame(points))
        .mark_circle(size=62, opacity=0.9)
        .encode(
            x=alt.X("x:Q", scale=alt.Scale(domain=[0, 1]), axis=axis),
            y=alt.Y("y:Q", scale=alt.Scale(domain=[0, 1]), axis=axis),
            color=alt.Color("cluster:N", scale=scale, legend=None),
            tooltip=["cluster:N"],
        )
    )

    return (
        alt.layer(blob_layer, point_layer)
        .properties(height=270)
        .configure_view(strokeWidth=0)
        .configure_axis(grid=False)
    )


def render_cluster_legend(counts):
    rows = "".join(
        f'<div class="legend-row">'
        f'<span class="legend-swatch" style="background:{CLUSTER_COLORS[i % len(CLUSTER_COLORS)]}"></span>'
        f"Cluster {cluster}<span class=\"legend-count\">{count} candidates</span></div>"
        for i, (cluster, count) in enumerate(counts.items())
    )
    st.markdown(f'<div class="legend">{rows}</div>', unsafe_allow_html=True)


# --------------------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------------------
def page_dashboard(api_url, similar_top_k):
    render_hero()

    upload_left, upload_right = st.columns(2, gap="medium")
    with upload_left:
        with st.container(border=True):
            st.markdown('<p class="card-title">1. Upload Job Description</p>', unsafe_allow_html=True)
            st.markdown(
                '<p class="card-sub">Drag &amp; drop a job description file here</p>',
                unsafe_allow_html=True,
            )
            jd_file = st.file_uploader(
                "Job description file",
                type=["txt", "pdf", "docx"],
                key="dash_jd",
                label_visibility="collapsed",
            )
            st.markdown('<p class="card-hint">Supports .txt, .pdf, .docx</p>', unsafe_allow_html=True)

    with upload_right:
        with st.container(border=True):
            st.markdown('<p class="card-title">2. Upload Resumes</p>', unsafe_allow_html=True)
            st.markdown(
                '<p class="card-sub">Drag &amp; drop multiple resume files here</p>',
                unsafe_allow_html=True,
            )
            resume_files = st.file_uploader(
                "Resume files",
                type=["pdf", "docx", "txt"],
                accept_multiple_files=True,
                key="dash_resumes",
                label_visibility="collapsed",
            )
            st.markdown(
                '<p class="card-hint">Supports .pdf, .docx (multiple files)</p>',
                unsafe_allow_html=True,
            )

    with st.container(border=True):
        select_col, run_col = st.columns([3, 1], gap="medium")
        titles = [job["title"] for job in st.session_state["jobs"]]
        with select_col:
            selected = st.selectbox("Select Job", titles, key="dash_job")
        with run_col:
            st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
            run = st.button("▶  Run Screening", type="primary", use_container_width=True)

    if run:
        job = next((j for j in st.session_state["jobs"] if j["title"] == selected), None)
        description = extract_text(jd_file) or (job or {}).get("description", "")
        if not resume_files:
            st.warning("Upload at least one resume before running the screening.")
        elif not description.strip():
            st.warning("Upload a job description file or add a description on the Jobs page.")
        else:
            try:
                with st.spinner("Screening resumes…"):
                    run_screening(api_url, selected, description, resume_files, similar_top_k)
                st.success(f"Screened {len(resume_files)} resume(s) for {selected}.")
            except requests.HTTPError as error:
                st.error(f"Backend returned {error.response.status_code}: {error.response.text[:400]}")
            except requests.RequestException as error:
                st.error(f"Could not reach the backend: {error}")

    results = st.session_state["screening_results"]
    render_stats(compute_stats(results))

    left, right = st.columns([1.55, 1], gap="medium")
    with left:
        with st.container(border=True):
            head_left, head_right = st.columns([2, 1])
            head_left.markdown(
                '<p class="card-title">Top Matched Candidates</p>', unsafe_allow_html=True
            )
            with head_right:
                if st.button("View All Candidates →", key="all_candidates", use_container_width=True):
                    st.session_state["page"] = "Candidates"
                    st.rerun()
            if results:
                render_candidate_table(results, limit=5, key_prefix="dash")
            else:
                render_empty("📄", "Upload resumes and run a screening to see ranked candidates.")

    with right:
        with st.container(border=True):
            head_left, head_right = st.columns([2, 1])
            head_left.markdown('<p class="card-title">Candidate Clusters</p>', unsafe_allow_html=True)
            with head_right:
                if st.button("View All Clusters →", key="all_clusters", use_container_width=True):
                    st.session_state["page"] = "Clusters"
                    st.rerun()
            counts = cluster_counts(results)
            if counts:
                st.altair_chart(cluster_chart(counts), use_container_width=True)
                render_cluster_legend(counts)
            else:
                render_empty("🧩", "Clusters appear once candidates have been screened.")


def page_screen(api_url, similar_top_k):
    with st.container(border=True):
        st.markdown('<p class="card-title">Screening Setup</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="card-sub">Describe the role, attach resumes and run the model</p>',
            unsafe_allow_html=True,
        )

        titles = [job["title"] for job in st.session_state["jobs"]]
        preset = st.selectbox("Start from a saved job", ["— none —"] + titles, key="screen_preset")
        default_description = ""
        default_title = "Graphic Designer"
        if preset != "— none —":
            job = next((j for j in st.session_state["jobs"] if j["title"] == preset), None)
            if job:
                default_title = job["title"]
                default_description = job["description"]

        job_title = st.text_input("Job Title", value=default_title, key=f"title_{preset}")
        job_description = st.text_area(
            "Job Description", value=default_description, height=240, key=f"desc_{preset}"
        )
        uploaded_files = st.file_uploader(
            "Resumes",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            key="screen_resumes",
        )
        submitted = st.button("🚀  Screen Resumes", type="primary")

    if submitted:
        if not uploaded_files:
            st.warning("Upload at least one resume.")
        elif not job_description.strip():
            st.warning("Add a job description.")
        else:
            try:
                with st.spinner("Screening resumes…"):
                    run_screening(
                        api_url, job_title, job_description, uploaded_files, similar_top_k
                    )
                st.success(f"Screened {len(uploaded_files)} resume(s).")
            except requests.HTTPError as error:
                st.error(f"Backend returned {error.response.status_code}: {error.response.text[:400]}")
            except requests.RequestException as error:
                st.error(f"Could not reach the backend: {error}")

    results = st.session_state["screening_results"]
    if not results:
        return

    st.markdown("### Results")
    stats = compute_stats(results)
    needs_review = sum(1 for r in results if r.get("pre_screen") == "NEEDS_REVIEW")
    summary = st.columns(3)
    summary[0].metric("Total Resumes", stats["total"])
    summary[1].metric(
        "Average Match Score",
        f"{stats['average'] * 100:.2f}%" if stats["average"] is not None else "N/A",
    )
    summary[2].metric("Needs Review", needs_review)

    for index, result in enumerate(sorted_results(results), start=1):
        with st.container(border=True):
            st.markdown(
                f'<p class="card-title">{index}. {candidate_name(result)}'
                f' <span class="pill {pill_class(to_unit_score(result.get("match_score")))}">'
                f'{percentage_text(result.get("match_score"))}</span></p>',
                unsafe_allow_html=True,
            )
            metrics = st.columns(4)
            metrics[0].metric("Match Score", percentage_text(result.get("match_score")))
            metrics[1].metric("Pre-Screen", str(result.get("pre_screen") or "N/A"))
            metrics[2].metric("Experience", experience_text(result))
            metrics[3].metric("Cluster", str(result.get("cluster") if result.get("cluster") is not None else "N/A"))

            skill_left, skill_right = st.columns(2)
            with skill_left:
                st.markdown("**Matched skills**")
                matched = result.get("matched_skills") or []
                st.markdown(
                    "".join(f'<span class="skill-chip ok">{s}</span>' for s in matched) or "—",
                    unsafe_allow_html=True,
                )
            with skill_right:
                st.markdown("**Missing skills**")
                missing = result.get("missing_skills") or []
                st.markdown(
                    "".join(f'<span class="skill-chip miss">{s}</span>' for s in missing) or "—",
                    unsafe_allow_html=True,
                )

            education = result.get("education")
            if education is not None:
                st.caption(f"Education: {education}")

            with st.expander("Model Explanation"):
                st.write(
                    {
                        "experience_score": result.get("experience_score"),
                        "candidate_experience_years": result.get("candidate_experience_years"),
                        "required_experience_years": result.get("required_experience_years"),
                        "required_experience_display": result.get("required_experience_display"),
                        "pre_screen_ready": result.get("pre_screen_ready"),
                        "positive_factors": result.get("positive_factors"),
                        "review_flags": result.get("review_flags"),
                    }
                )

    with st.expander("🔎 Raw API Response"):
        st.json(st.session_state.get("raw_response") or {})


def page_jobs():
    with st.container(border=True):
        st.markdown('<p class="card-title">Add a Job</p>', unsafe_allow_html=True)
        title = st.text_input("Job title", key="new_job_title")
        description = st.text_area("Job description", height=180, key="new_job_description")
        if st.button("Save Job", type="primary"):
            if title.strip() and description.strip():
                st.session_state["jobs"].append(
                    {"title": title.strip(), "description": description.strip()}
                )
                st.success(f"Saved “{title.strip()}”.")
                st.rerun()
            else:
                st.warning("A job needs both a title and a description.")

    with st.container(border=True):
        st.markdown('<p class="card-title">Saved Jobs</p>', unsafe_allow_html=True)
        for index, job in enumerate(st.session_state["jobs"]):
            cols = st.columns([3, 1])
            cols[0].markdown(
                f'<div class="td-strong">{job["title"]}</div>'
                f'<div class="td-muted">{job["description"][:120].replace(chr(10), " ")}…</div>',
                unsafe_allow_html=True,
            )
            with cols[1]:
                if st.button("Screen this job", key=f"use_job_{index}", use_container_width=True):
                    st.session_state["page"] = "Screen Resumes"
                    st.session_state["screen_preset"] = job["title"]
                    st.rerun()
            st.markdown('<div class="rowline"></div>', unsafe_allow_html=True)


def page_candidates():
    results = st.session_state["screening_results"]
    with st.container(border=True):
        st.markdown('<p class="card-title">All Candidates</p>', unsafe_allow_html=True)
        job = st.session_state.get("screened_job")
        if job:
            st.markdown(f'<p class="card-sub">Ranked for {job}</p>', unsafe_allow_html=True)
        if results:
            render_candidate_table(results, key_prefix="cand")
        else:
            render_empty("👥", "No candidates yet. Run a screening from the dashboard.")

    selected = st.session_state.get("selected_candidate")
    if selected and results:
        match = next((r for r in results if r.get("resume_filename") == selected), None)
        if match:
            with st.container(border=True):
                st.markdown(
                    f'<p class="card-title">{candidate_name(match)}</p>', unsafe_allow_html=True
                )
                metrics = st.columns(4)
                metrics[0].metric("Match Score", percentage_text(match.get("match_score")))
                metrics[1].metric("Pre-Screen", str(match.get("pre_screen") or "N/A"))
                metrics[2].metric("Experience", experience_text(match))
                metrics[3].metric(
                    "Cluster",
                    str(match.get("cluster") if match.get("cluster") is not None else "N/A"),
                )
                st.markdown("**Matched skills**")
                st.markdown(
                    "".join(
                        f'<span class="skill-chip ok">{s}</span>'
                        for s in (match.get("matched_skills") or [])
                    )
                    or "—",
                    unsafe_allow_html=True,
                )
                st.markdown("**Missing skills**")
                st.markdown(
                    "".join(
                        f'<span class="skill-chip miss">{s}</span>'
                        for s in (match.get("missing_skills") or [])
                    )
                    or "—",
                    unsafe_allow_html=True,
                )


def page_clusters():
    results = st.session_state["screening_results"]
    counts = cluster_counts(results)

    with st.container(border=True):
        st.markdown('<p class="card-title">Candidate Clusters</p>', unsafe_allow_html=True)
        if not counts:
            render_empty("🧩", "Clusters appear once candidates have been screened.")
            return
        chart_col, legend_col = st.columns([2, 1], gap="medium")
        with chart_col:
            st.altair_chart(cluster_chart(counts), use_container_width=True)
        with legend_col:
            render_cluster_legend(counts)

    for cluster in counts:
        members = [r for r in results if str(r.get("cluster")) == cluster]
        with st.container(border=True):
            st.markdown(
                f'<p class="card-title">Cluster {cluster}</p>'
                f'<p class="card-sub">{len(members)} candidates</p>',
                unsafe_allow_html=True,
            )
            render_candidate_table(members, key_prefix=f"cl{cluster}")


def page_analytics():
    results = st.session_state["screening_results"]
    render_stats(compute_stats(results))

    if not results:
        with st.container(border=True):
            render_empty("📊", "Analytics populate after your first screening run.")
        return

    left, right = st.columns(2, gap="medium")

    with left:
        with st.container(border=True):
            st.markdown('<p class="card-title">Match Score Distribution</p>', unsafe_allow_html=True)
            frame = pd.DataFrame(
                {
                    "candidate": [candidate_name(r) for r in sorted_results(results)],
                    "score": [to_unit_score(r.get("match_score")) or 0 for r in sorted_results(results)],
                }
            )
            chart = (
                alt.Chart(frame)
                .mark_bar(cornerRadiusEnd=5, color="#3B82F6", size=18)
                .encode(
                    x=alt.X("score:Q", scale=alt.Scale(domain=[0, 1]), title="Match score"),
                    y=alt.Y("candidate:N", sort="-x", title=None),
                    tooltip=["candidate:N", alt.Tooltip("score:Q", format=".2f")],
                )
                .properties(height=max(200, 30 * len(frame)))
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(chart, use_container_width=True)

    with right:
        with st.container(border=True):
            st.markdown('<p class="card-title">Most Common Matched Skills</p>', unsafe_allow_html=True)
            tally = {}
            for result in results:
                for skill in result.get("matched_skills") or []:
                    key = str(skill).strip().title()
                    tally[key] = tally.get(key, 0) + 1
            if not tally:
                render_empty("🧠", "No matched skills reported yet.")
            else:
                frame = pd.DataFrame(
                    sorted(tally.items(), key=lambda item: item[1], reverse=True)[:12],
                    columns=["skill", "count"],
                )
                chart = (
                    alt.Chart(frame)
                    .mark_bar(cornerRadiusEnd=5, color="#8B5CF6", size=18)
                    .encode(
                        x=alt.X("count:Q", title="Candidates"),
                        y=alt.Y("skill:N", sort="-x", title=None),
                        tooltip=["skill:N", "count:Q"],
                    )
                    .properties(height=max(200, 30 * len(frame)))
                    .configure_view(strokeWidth=0)
                )
                st.altair_chart(chart, use_container_width=True)

    with st.container(border=True):
        st.markdown('<p class="card-title">Screening Table</p>', unsafe_allow_html=True)
        table = pd.DataFrame(
            [
                {
                    "Candidate": candidate_name(r),
                    "File": r.get("resume_filename"),
                    "Match Score": to_unit_score(r.get("match_score")),
                    "Pre-Screen": r.get("pre_screen"),
                    "Experience": experience_text(r),
                    "Cluster": r.get("cluster"),
                    "Matched Skills": len(r.get("matched_skills") or []),
                    "Missing Skills": len(r.get("missing_skills") or []),
                }
                for r in sorted_results(results)
            ]
        )
        st.dataframe(table, use_container_width=True, hide_index=True)


# --------------------------------------------------------------------------------------
# Shell
# --------------------------------------------------------------------------------------
def main():
    st.markdown(CSS, unsafe_allow_html=True)

    st.session_state.setdefault("page", "Dashboard")
    st.session_state.setdefault("screening_results", [])
    st.session_state.setdefault("raw_response", None)
    st.session_state.setdefault("jobs", list(DEFAULT_JOBS))
    st.session_state.setdefault("selected_candidate", None)

    with st.sidebar:
        st.markdown(
            '<div class="brand"><div class="brand-logo">📄</div>'
            '<div class="brand-name">AI Resume Screener</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="nav-label">Menu</div>', unsafe_allow_html=True)
        for label, icon in NAV_ITEMS:
            active = st.session_state["page"] == label
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{label}",
                use_container_width=True,
                type="primary" if active else "secondary",
            ):
                st.session_state["page"] = label
                st.rerun()

        st.markdown('<div class="nav-label">Backend</div>', unsafe_allow_html=True)
        api_url = st.text_input(
            "FastAPI URL", value=resolve_api_url(), label_visibility="collapsed"
        ).rstrip("/")
        similar_top_k = st.slider("Similar resumes (top K)", 1, 10, 5)
        st.markdown(
            '<div class="side-note"><b>Backend</b><br>FastAPI · Random Forest<br>'
            "Sentence Transformers · FAISS · KMeans</div>",
            unsafe_allow_html=True,
        )

    page = st.session_state["page"]
    render_topbar(page, check_api(api_url))

    if page == "Dashboard":
        page_dashboard(api_url, similar_top_k)
    elif page == "Screen Resumes":
        page_screen(api_url, similar_top_k)
    elif page == "Jobs":
        page_jobs()
    elif page == "Candidates":
        page_candidates()
    elif page == "Clusters":
        page_clusters()
    else:
        page_analytics()


main()
