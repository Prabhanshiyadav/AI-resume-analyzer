# app.py  – AI‑Resume‑Analyzer UI v2.0
import streamlit as st
import matplotlib.pyplot as plt

from utils import (
    extract_text_from_pdf,
    extract_name,
    extract_contact_info,
    extract_skills,
    generate_summary,
)
from model import calculate_bert_similarity

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
st.title("📄 AI Resume Analyzer  — v2.0")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
jd_text     = st.text_area("Paste Job Description ✍️", height=150)

with st.sidebar:
    st.header("🔧 Overrides")
    override_name = st.text_input("Candidate Name", placeholder="Optional: e.g., Prabhanshi Yadav")
    override_role = st.text_input("Target Role", placeholder="Optional: e.g., Machine Learning Engineer")



# ──────────────────────────
if resume_file and jd_text:
    with st.spinner("Analyzing..."):
        resume_text = extract_text_from_pdf(resume_file)
        similarity = calculate_bert_similarity(resume_text, jd_text)

        matched_skills, missing_skills = extract_skills(resume_text)

        # ⬇️ Override or extract name/role
        name = override_name if override_name else extract_name(resume_text)
        role = override_role if override_role else "Machine Learning Engineer"

        summary = generate_summary(name, role, similarity, matched_skills, missing_skills)

        st.success(f"Match Score: {similarity * 100:.2f}%")
        st.text_area("📄 Result Summary", value=summary, height=300)

        st.download_button(
            label="📥 Download Report",
            data=summary,
            file_name="resume_match_report.txt",
            mime="text/plain"
        )
