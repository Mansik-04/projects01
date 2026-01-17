import streamlit as st
import pandas as pd
import pdfplumber
from fpdf import FPDF
from utils import clean_text, extract_resume_details, extract_skills, highlight_skills

# ------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------
st.set_page_config(
    page_title="AI Resume Screening & ATS Matcher",
    page_icon="📄",
    layout="wide"
)

# ------------------------------------------------------
# LOAD JOB DATA
# ------------------------------------------------------
jobs_df = pd.read_csv("data/training_data.csv")
jobs_df["clean"] = jobs_df["job_description"].apply(clean_text)

# ------------------------------------------------------
# PDF GENERATOR (FPDF SAFE VERSION)
# ------------------------------------------------------
def generate_pdf_report(name, email, phone, best, ats_score, resume_skills):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 12, "ATS Resume Screening Report", ln=True, align="C")
    pdf.ln(8)

    # Candidate details
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Candidate Details", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Name: {name}", ln=True)
    pdf.cell(0, 8, f"Email: {email}", ln=True)
    pdf.cell(0, 8, f"Phone: {phone}", ln=True)
    pdf.ln(5)

    # Best match
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Best Job Match", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Position: {best['position_title']}", ln=True)
    pdf.cell(0, 8, f"Company: {best['company_name']}", ln=True)
    pdf.cell(0, 8, f"Score: {round(best['Final_Score'], 2)}", ln=True)
    pdf.ln(5)

    # ATS score
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "ATS Score", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"{ats_score} / 100", ln=True)
    pdf.ln(5)

    # Skills
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Skills Detected", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, ", ".join(resume_skills))

    return pdf.output(dest="S").encode("latin1")

# ------------------------------------------------------
# HEADER
# ------------------------------------------------------
st.markdown("<h1>📄 AI Resume Screening & ATS Matcher</h1>", unsafe_allow_html=True)

# ------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------
with st.sidebar:
    st.header("⚙ Matching Controls")

    text_weight = st.slider("Text Similarity Weight", 0.0, 1.0, 0.55, 0.01)
    skill_weight = st.slider("Skill Match Weight", 0.0, 1.0, 0.30, 0.01)
    title_weight = st.slider("Title Weight", 0.0, 1.0, 0.48, 0.01)

# ------------------------------------------------------
# FILE UPLOAD
# ------------------------------------------------------
uploaded_file = st.file_uploader("Upload Resume (.txt or .pdf)")

if uploaded_file:

    # ------------------------------------------------------
    # Extract resume text
    # ------------------------------------------------------
    if uploaded_file.name.endswith(".txt"):
        text = uploaded_file.read().decode("utf-8", errors="ignore")

    elif uploaded_file.name.endswith(".pdf"):
        pdf = pdfplumber.open(uploaded_file)
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    else:
        st.error("❌ Please upload a valid .txt or .pdf resume.")
        st.stop()

    # ------------------------------------------------------
    # Clean resume text
    # ------------------------------------------------------
    cleaned_resume = clean_text(text)

    # ------------------------------------------------------
    # Extract personal details
    # ------------------------------------------------------
    extracted = extract_resume_details(text)
    name = extracted.get("name", "Not Found")
    email = extracted.get("email", "Not Found")
    phone = extracted.get("phone", "Not Found")

    # ------------------------------------------------------
    # Extract skills
    # ------------------------------------------------------
    resume_skills = extract_skills(cleaned_resume)

    # ------------------------------------------------------
    # MATCHING SCORES
    # ------------------------------------------------------
    jobs_df["text_score"] = jobs_df["clean"].apply(
        lambda x: len(set(x.split()) & set(cleaned_resume.split())) /
                  max(len(set(cleaned_resume.split())), 1)
    )

    jobs_df["skill_score"] = jobs_df["clean"].apply(
        lambda x: len(set(resume_skills) & set(x.split()))
    )

    jobs_df["title_score"] = jobs_df["position_title"].apply(
        lambda t: 1 if any(word.lower() in t.lower() for word in resume_skills) else 0
    )

    jobs_df["Final_Score"] = (
            jobs_df["text_score"] * text_weight +
            jobs_df["skill_score"] * skill_weight +
            jobs_df["title_score"] * title_weight
    ) * 100

    # ------------------------------------------------------
    # BEST MATCH
    # ------------------------------------------------------
    best = jobs_df.sort_values("Final_Score", ascending=False).iloc[0]

    st.subheader("🎯 Best Job Match")
    st.write(f"**Position:** {best['position_title']}")
    st.write(f"**Company:** {best['company_name']}")
    st.write(f"**Score:** {round(best['Final_Score'], 2)}")

    # ------------------------------------------------------
    # ATS SCORE
    # ------------------------------------------------------
    ats_score = max(40, min(90, round(best["Final_Score"], 2)))

    st.subheader("🛠 ATS Score")
    st.success(f"Your ATS Score: **{ats_score} / 100**")

    # ------------------------------------------------------
    # SKILLS DETECTED
    # ------------------------------------------------------
    st.subheader("🧩 Skills Detected in Resume")
    st.write(", ".join(resume_skills))

    # ------------------------------------------------------
    # HIGHLIGHTED JOB DESCRIPTION
    # ------------------------------------------------------
    st.subheader("📝 Highlighted Job Description")
    highlighted = highlight_skills(best["job_description"], resume_skills)
    st.markdown(highlighted, unsafe_allow_html=True)

    # ------------------------------------------------------
    # TOP 5 RECOMMENDATIONS
    # ------------------------------------------------------
    st.subheader("📊 Top 5 Job Recommendations")
    top5 = jobs_df.sort_values("Final_Score", ascending=False).head(5)
    st.dataframe(top5[["position_title", "company_name", "Final_Score"]])

    # ------------------------------------------------------
    # CSV DOWNLOAD
    # ------------------------------------------------------
    csv = top5.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Results CSV", csv, "results.csv", "text/csv")

    # ------------------------------------------------------
    # PDF DOWNLOAD (NO ERRORS)
    # ------------------------------------------------------
    st.subheader("📄 Download PDF Report")

    pdf_bytes = generate_pdf_report(
        name, email, phone, best, ats_score, resume_skills
    )

    st.download_button(
        label="⬇️ Download PDF Report",
        data=pdf_bytes,
        file_name="ATS_Report.pdf",
        mime="application/pdf"
    )

else:
    st.info("📥 Upload a resume to begin analysis.")
