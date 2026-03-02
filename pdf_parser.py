import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
    return text


if __name__ == "__main__":
    raw_text = extract_text_from_pdf("resume.pdf")
    print("----- RAW TEXT FROM PDF -----")
    print(raw_text)
