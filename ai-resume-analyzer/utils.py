"""
utils.py – helpers for AI‑Resume‑Analyzer  ❱❱  v2.0
────────────────────────────────────────────────────
• extract_text_from_pdf   – read text from PDF (PyMuPDF)
• parse_sections          – split resume into sections by common headings
• extract_name            – PERSON entity in header / contact block
• extract_contact_info    – regex email + phone
• extract_skills          – PhraseMatcher on skills section first, then full doc
• generate_summary        – result block incl. contact info
"""

import re
import fitz                          # PyMuPDF
import spacy
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")

SKILL_KEYWORDS = [  # expand as you like
    "python", "machine learning", "deep learning", "tensorflow", "pytorch",
    "nlp", "data analysis", "sql", "docker", "aws", "flask", "deployment",
    "git", "linux", "scikit-learn", "streamlit", "pandas", "numpy", "ci/cd",
]

_phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
_phrase_matcher.add("SKILLS", [nlp.make_doc(k) for k in SKILL_KEYWORDS])

# ───────────────────────────────────────────────────────────────
def extract_text_from_pdf(file_obj) -> str:
    doc = fitz.open(stream=file_obj.read(), filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

# ───────────────────────────────────────────────────────────────
_section_re = re.compile(
    r"^\s*(skills?|technical skills?|experience|work experience|education|projects?)\s*$",
    re.I | re.M,
)

def parse_sections(text: str) -> dict[str, str]:
    """
    Split resume into sections using common headings.
    Returns dict {heading_lower: section_text}.
    """
    parts = _section_re.split(text)
    if len(parts) <= 1:
        return {"full": text}

    sections = {}
    # parts comes like ["", "Skills", "...", "Experience", "...", ...]
    for i in range(1, len(parts), 2):
        heading = parts[i].strip().lower()
        body    = parts[i + 1]
        sections[heading] = body
    return sections or {"full": text}

# ───────────────────────────────────────────────────────────────
_email_re  = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_phone_re  = re.compile(r"\+?\d[\d\s\-()]{7,}\d")

def extract_contact_info(text: str) -> tuple[str | None, str | None]:
    email  = _email_re.search(text)
    phone  = _phone_re.search(text)
    return (email.group(0) if email else None, phone.group(0) if phone else None)

def extract_name(text: str) -> str:
    header = "\n".join(text.splitlines()[:15])
    doc    = nlp(header)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return re.sub(r"\s{2,}", " ", ent.text.strip())
    return "Candidate"

# ───────────────────────────────────────────────────────────────
def extract_skills(text: str):
    sects = parse_sections(text)
    # Prefer "skills" section if exists
    skills_scope = sects.get("skills", sects.get("technical skills", text))

    doc = nlp(skills_scope.lower())
    matches = _phrase_matcher(doc)
    matched = {doc[s:e].text.lower() for _, s, e in matches}
    missing = set(SKILL_KEYWORDS) - matched
    return sorted(matched), sorted(missing)

# ───────────────────────────────────────────────────────────────
def generate_summary(
    name: str,
    role: str,
    similarity: float,
    matched: list[str],
    missing: list[str],
    email: str | None = None,
    phone: str | None = None,
) -> str:
    skills_pct  = round(len(matched) / len(SKILL_KEYWORDS) * 100, 2)
    jd_pct      = round(similarity * 100, 2)
    overall_pct = round(((similarity * 0.6) + (skills_pct / 100 * 0.4)) * 100, 2)

    contact_lines = []
    if email: contact_lines.append(f"Email: {email}")
    if phone: contact_lines.append(f"Phone: {phone}")
    contact_block = "\n".join(contact_lines) + ("\n" if contact_lines else "")

    missing_str = ", ".join(missing) if missing else "None"

    return (
        f"{contact_block}"
        f"Name: {name}\n"
        f"Role: {role}\n\n"
        "Score Summary:\n"
        f"- Skills Match: {skills_pct}%\n"
        f"- JD Coverage: {jd_pct}%\n"
        f"- Overall Match: {overall_pct}%\n\n"
        "Missing Keywords:\n"
        f"- {missing_str}"
    )
