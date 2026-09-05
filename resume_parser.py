from pypdf import PdfReader

pdf_path = "resumes/RESUME.pdf"

reader = PdfReader(pdf_path)

resume_text = ""

for page in reader.pages:
    text = page.extract_text()

    if text:
        resume_text += text + "\n"

print(resume_text)