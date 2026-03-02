def load_skills(csv_path):
    with open(csv_path, "r", encoding="utf-8") as file:
        return [line.strip().lower() for line in file if line.strip()]


def extract_skills(cleaned_text, skills_list):
    return [skill for skill in skills_list if skill in cleaned_text]


if __name__ == "__main__":
    from text_cleaner import clean_text
    from pdf_parser import extract_text_from_pdf

    text = extract_text_from_pdf("resume.pdf")
    cleaned = clean_text(text)

    skills = load_skills("skills.csv")
    print("TOTAL SKILLS LOADED:", len(skills))

    found_skills = extract_skills(cleaned, skills)

    print("\nExtracted Skills:")
    for s in found_skills:
        print("✔", s)
