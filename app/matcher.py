KNOWN_SKILLS = [
    "python", "java", "c++", "fastapi", "flask", "django",
    "sql", "mysql", "postgresql", "sqlite",
    "react", "html", "css", "javascript",
    "docker", "aws", "git",
    "excel", "power bi", "tableau", "pandas", "numpy",
    "machine learning", "data analysis"
]


SKILL_CATEGORIES = {
    "backend": ["fastapi", "flask", "django"],
    "programming": ["python", "java", "c++", "javascript"],
    "database": ["sql", "mysql", "postgresql", "sqlite"],
    "frontend": ["react", "html", "css", "javascript"],
    "devops": ["docker", "aws", "git"],
    "data": ["excel", "power bi", "tableau", "pandas", "numpy", "machine learning", "data analysis"]
}


def normalize_skills(skills):
    return list(set(skill.lower().strip() for skill in skills))


def extract_skills(text: str):
    text = text.lower()
    found = []

    for skill in KNOWN_SKILLS:
        if skill in text:
            found.append(skill)

    return normalize_skills(found)


def keyword_match(resume_skills, job_skills):
    resume_skills = normalize_skills(resume_skills)
    job_skills = normalize_skills(job_skills)

    matched = list(set(resume_skills) & set(job_skills))
    missing = list(set(job_skills) - set(resume_skills))

    percent = int(len(matched) / len(job_skills) * 100) if job_skills else 0

    return matched, missing, percent


def category_match(resume_skills, job_skills):
    resume_skills = normalize_skills(resume_skills)
    job_skills = normalize_skills(job_skills)

    matched_categories = []
    required_categories = []

    for category, skills in SKILL_CATEGORIES.items():
        resume_has_category = any(skill in resume_skills for skill in skills)
        job_needs_category = any(skill in job_skills for skill in skills)

        if job_needs_category:
            required_categories.append(category)

        if resume_has_category and job_needs_category:
            matched_categories.append(category)

    percent = int(len(matched_categories) / len(required_categories) * 100) if required_categories else 0

    return matched_categories, percent


def calculate_final_score(keyword_score, category_score, ai_score):
    return int(
        (keyword_score * 0.4) +
        (category_score * 0.3) +
        (ai_score * 0.3)
    )