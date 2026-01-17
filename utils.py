import re
import nltk
import pdfplumber
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('omw-1.4')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# ---------------------------
# CLEAN TEXT FUNCTION
# ---------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    words = text.split()

    cleaned = []
    for w in words:
        if w not in stop_words:
            cleaned.append(lemmatizer.lemmatize(w))

    return " ".join(cleaned)

# ---------------------------
# PDF EXTRACTOR
# ---------------------------
def extract_pdf_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            p_text = page.extract_text()
            if p_text:
                text += p_text + " "
    return text
def extract_resume_details(text):
    name = "Not Found"
    email = "Not Found"
    phone = "Not Found"

    # NAME extraction (simple heuristic)
    lines = text.strip().split("\n")
    if len(lines) > 0:
        first_line = lines[0]
        if len(first_line.split()) <= 4:
            name = first_line.strip().title()

    # EMAIL extraction
    match_email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    if match_email:
        email = match_email.group(0)

    # PHONE extraction
    match_phone = re.search(r"\b\d{10}\b", text)
    if match_phone:
        phone = match_phone.group(0)

    return {
        "name": name,
        "email": email,
        "phone": phone
    }

# ---------------------------
# SKILL DICTIONARY
# ---------------------------
skill_dictionary = {
    "python": ["python"],
    "sql": ["sql", "mysql", "postgres", "oracle"],
    "power bi": ["power bi", "powerbi"],
    "excel": ["excel", "spreadsheet"],
    "tableau": ["tableau"],
    "ml": ["machine learning", "ml"],
    "dl": ["deep learning", "neural network", "dl"],
    "nlp": ["nlp", "natural language processing"],
    "statistics": ["statistics", "statistical"],
    "data analysis": ["data analysis", "data analyst"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "matplotlib": ["matplotlib"],
    "seaborn": ["seaborn"],
    "git": ["git", "github"],
    "jira": ["jira"],
    "tensorflow": ["tensorflow"],
    "sklearn": ["scikit", "sklearn"],
}

def extract_skills(text):
    text = text.lower()
    extracted = []

    for skill, keywords in skill_dictionary.items():
        for kw in keywords:
            if kw in text:
                extracted.append(skill.title())
                break

    return list(set(extracted))

# ---------------------------
# RESUME PARSER
# ---------------------------
def extract_contact_details(text):
    name = text.split("\n")[0].strip()

    email_pattern = r"\S+@\S+\.\S+"
    phone_pattern = r"\+?\d[\d\s\-]{8,15}"

    email = re.findall(email_pattern, text)
    phone = re.findall(phone_pattern, text)

    return {
        "name": name,
        "email": email[0] if email else "Not Found",
        "phone": phone[0] if phone else "Not Found"
    }

# ---------------------------
# HIGHLIGHT SKILLS IN TEXT
# ---------------------------
def highlight_text(description, skills):
    for skill in skills:
        pattern = re.compile(skill, re.IGNORECASE)
        description = pattern.sub(
            f"<mark style='background-color: #fff176'>{skill}</mark>",
            description
        )
    return description
def highlight_skills(text, skills):
    highlighted = text

    for skill in skills:
        pattern = r"\b" + re.escape(skill) + r"\b"
        highlighted = re.sub(
            pattern,
            f"<mark><b>{skill}</b></mark>",
            highlighted,
            flags=re.IGNORECASE
        )

    return highlighted

