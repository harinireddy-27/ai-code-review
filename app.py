import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import time

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="AI Code Review Assistant",
    page_icon="🤖",
    layout="wide"
)
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------------------
# Sidebar
# ---------------------------------
st.sidebar.title("🤖 AI Code Review Assistant")

st.sidebar.success("Version 2.0")

st.sidebar.markdown("""
### Technologies Used

- Python
- Streamlit
- Groq AI
- Prompt Engineering
- ReportLab
""")

st.sidebar.info("""
### Tips

✔ Upload your code

✔ Or paste your code

✔ Click Review Code

✔ Download TXT Report

✔ Download PDF Report
""")

st.sidebar.divider()

st.sidebar.markdown("### 🚀 Features")

st.sidebar.write("✔ AI Code Review")
st.sidebar.write("✔ Error Detection")
st.sidebar.write("✔ Corrected Code")
st.sidebar.write("✔ PDF Report")
st.sidebar.write("✔ TXT Report")
st.sidebar.write("✔ File Upload")

st.sidebar.subheader("Project Progress")

st.sidebar.progress(100)

st.sidebar.success("Day 6 Completed")

# ---------------------------------
# Load Environment Variables
# ---------------------------------
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

# ---------------------------------
# PDF Function
# ---------------------------------
from io import BytesIO

def create_pdf(review):

    buffer = BytesIO()

    styles = getSampleStyleSheet()

    pdf = SimpleDocTemplate(buffer)

    story = []

    story.append(
        Paragraph(
            review.replace("\n", "<br/>"),
            styles["Normal"]
        )
    )

    pdf.build(story)

    buffer.seek(0)

    return buffer.getvalue()

# ---------------------------------
# Title
# ---------------------------------

st.markdown("""
# 🤖 AI Code Review Assistant

Analyze your Python, Java, and C++ code using AI.
Receive instant feedback, corrections, suggestions, and a quality score.
""")

st.info("""
### How to Use

1. Select Programming Language.

2. Upload a file or paste code.

3. Click Review Code.

4. Download the report.
""")

# ---------------------------------
# Language
# ---------------------------------
language = st.selectbox(
    "Select Programming Language",
    [
        "Python",
        "Java",
        "C",
        "C++",
        "JavaScript",
        "TypeScript",
        "HTML",
        "CSS",
        "SQL",
        "PHP",
        "C#",
        "Go",
        "Rust",
        "Swift",
        "Kotlin",
        "R",
        "MATLAB",
        "Scala",
        "Dart",
        "Ruby",
        "Perl",
        "Shell Script (Bash)"
    ]
)

# ---------------------------------
# File Upload
# ---------------------------------
uploaded_file = st.file_uploader(
    "📂 Upload your code",
    type=[
        "py", "java", "c", "cpp", "js", "ts",
        "html", "css", "sql", "php", "cs",
        "go", "rs", "swift", "kt", "r",
        "m", "scala", "dart", "rb", "pl",
        "sh", "txt"
    ]
)

code=""

if uploaded_file is not None:

    code = uploaded_file.read().decode("utf-8")

    st.success("✅ File Uploaded Successfully")

    st.write("File Name:",uploaded_file.name)

    st.write("File Size:",uploaded_file.size,"bytes")

# ---------------------------------
# Text Area
# ---------------------------------
code = st.text_area(
    "Paste your code",
    value=code,
    height=350
)

# ---------------------------------
# Statistics
# ---------------------------------
col1,col2,col3 = st.columns(3)

col1.metric("Characters",len(code))

col2.metric("Lines",len(code.splitlines()))

col3.metric("Words",len(code.split()))

if st.button("🧹 Clear Code"):
    st.rerun()
# ---------------------------------
# Review Button
# ---------------------------------
st.divider()

st.subheader("💻 AI Code Generator")

generation_prompt = st.text_area(
    "Describe the code you want",
    placeholder="Example: Write a Python program to implement Binary Search."
)

if st.button("🚀 Generate Code"):

    if generation_prompt.strip() == "":
        st.warning("Please enter a prompt.")

    else:

        with st.spinner("Generating code..."):

            prompt = f"""
You are an expert {language} programmer.

Generate clean, professional, well-commented {language} code.

Requirements:
- Write only the code.
- Add meaningful comments.
- Follow best coding practices.
- Do not explain anything outside the code.

User Request:

{generation_prompt}
"""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            generated_code = response.choices[0].message.content

            st.success("✅ Code Generated Successfully")

            st.code(generated_code, language.lower())

            st.download_button(
                "⬇ Download Generated Code",
                generated_code,
                file_name=f"generated_code.{language.lower()}",
                mime="text/plain"
            )

            if st.button("Use Generated Code for Review"):
                st.session_state.generated_code = generated_code
                st.rerun()
# ---------------------------------
# Review Button
# ---------------------------------
if st.button("Review Code"):

    if code.strip() == "":
        st.warning("⚠ Please enter some code.")
    else:

        try:

            prompt = f"""
You are an expert software engineer and code reviewer.

Analyze the following {language} code carefully.

VERY IMPORTANT RULES:

1. If the code has NO errors, NEVER say "ERROR FOUND".
2. If the code is correct, respond exactly in this format:

✅ Code Status:
No Errors Found

🎯 Output:
(Tell the expected output)

💡 Suggestions:
(2 or 3 suggestions)

⭐ Code Quality Score:
(score out of 10)

------------------------------------------------

3. If the code HAS an error, respond exactly in this format:

🔴 Error Found

Error Type:
(Name of error)

Error Explanation:
(Simple explanation)

Correct Code:

```{language}
(correct code)

Code:

{code}
"""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            review = response.choices[0].message.content
            st.session_state.history.append(review)
            st.subheader("🤖 AI Review")

            if "Error Found" in review:
                st.error("❌ Errors Found in the Code")
            else:
                st.success("✅ No Errors Found")

            st.markdown(review)

            st.download_button(
                "📄 Download TXT Report",
                review,
                file_name="AI_Code_Review_Report.txt"
            )

            pdf = create_pdf(review)

            st.download_button(
                "📕 Download PDF Report",
                pdf,
                file_name="AI_Code_Review_Report.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ---------------------------------
# Footer
# ---------------------------------

st.divider()
st.subheader("📜 Review History")

if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history), start=1):
        with st.expander(f"Review {i}"):
            st.markdown(item)

st.markdown("### 🚀 Project Features")

col1, col2 = st.columns(2)

with col1:
    st.success("✅ AI Code Review")
    st.success("✅ File Upload")
    st.success("✅ TXT Report")
    st.success("✅ PDF Report")

with col2:
    st.success("✅ Programming Language Selection")
    st.success("✅ Code Statistics")
    st.success("✅ Professional UI")
    st.success("✅ Groq AI Integration")

st.divider()

st.caption("🤖 Powered by Groq AI")
st.caption("💻 Developed by Harini")
st.caption("📌 Version 2.0")
st.caption("© 2026 AI Code Review Assistant")