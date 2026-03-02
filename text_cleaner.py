import re

STOPWORDS = {
    "the", "and", "is", "in", "to", "of", "for", "with",
    "on", "at", "by", "an", "be", "this", "that", "as",
    "are", "was", "were", "it"
}

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    words = text.split()
    filtered_words = [w for w in words if w not in STOPWORDS]

    return " ".join(filtered_words)


if __name__ == "__main__":
    from pdf_parser import extract_text_from_pdf

    raw = extract_text_from_pdf("resume.pdf")
    cleaned = clean_text(raw)

    print("----- CLEANED TEXT -----")
    print(cleaned)
