from fastapi import FastAPI, UploadFile, File, Form, Depends
from app.pdf_utils import clean_text, extract_text_from_pdf
from app.matcher import extract_skills, keyword_match, category_match, calculate_final_score
from app.ai_service import analyze_resume_with_ai
from app.schemas import AIResponse
import json
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models import Analysis
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.pdf_report import create_analysis_pdf
from dotenv import load_dotenv
load_dotenv()
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI resume analyzer v2",
    description="fastapi version with structured output and job matching",
    version="2.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Ai resume analyzer v2 is running"}



@app.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    job_description: str | None = Form(""),
    provider: str = Form("ollama"),
    db: Session = Depends(get_db)
    
):
    
    
    

    file_bytes = await file.read()

    text = extract_text_from_pdf(file_bytes)
    text = clean_text(text)

    resume_skills = extract_skills(text)
    job_skills = extract_skills(job_description)

    matched, missing, score = keyword_match(resume_skills, job_skills)

    matched_categories, category_score = category_match(resume_skills, job_skills)

    try:
      ai_result_raw = analyze_resume_with_ai(text, provider)
      ai_result = AIResponse(**ai_result_raw)
    except Exception as e:
      ai_result = AIResponse(
        score=50,
        summary=f"AI error: {str(e)}",
        suggestions=[],
        skills=[]

        
    )

    final_score = calculate_final_score(
        keyword_score=score,
        category_score=category_score,
        ai_score=ai_result.score
)
    new_analysis = Analysis(
    filename=file.filename,
    provider=provider,

    resume_skills=json.dumps(resume_skills),
    job_skills=json.dumps(job_skills),
    matched_skills=json.dumps(matched),
    missing_skills=json.dumps(missing),
    matched_categories=json.dumps(matched_categories),

    match_percent=score,
    category_score=category_score,
    final_score=final_score,
    ai_score=ai_result.score,

    summary=ai_result.summary,
    suggestions=json.dumps(ai_result.suggestions)
)
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    return {
    "analysis_id": new_analysis.id,
    "resume_skills": resume_skills,
    "job_skills": job_skills,
    "matched_skills": matched,
    "missing_skills": missing,
    "match_percent": score,
    "category_score": category_score,
    "matched_categories": matched_categories,
    "final_score": final_score,
    "ai_analysis": ai_result
}
@app.get("/results")
def get_results(db: Session = Depends(get_db)):
    results = db.query(Analysis).order_by(Analysis.id.desc()).all()

    return [
        {
            "id": item.id,
            "filename": item.filename,
            "provider": item.provider,
            "match_percent": item.match_percent,
            "category_score": item.category_score,
            "final_score": item.final_score,
            "ai_score": item.ai_score,
            "summary": item.summary,
            "created_at": item.created_at
        }
        for item in results
    ]
@app.get("/results/{analysis_id}")
def get_result_detail(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    item = db.query(Analysis).filter(Analysis.id == analysis_id).first()

    if not item:
        return {"error": "Analysis not found"}

    return {
        "id": item.id,
        "filename": item.filename,
        "provider": item.provider,
        "resume_skills": json.loads(item.resume_skills),
        "job_skills": json.loads(item.job_skills),
        "matched_skills": json.loads(item.matched_skills),
        "missing_skills": json.loads(item.missing_skills),
        "matched_categories": json.loads(item.matched_categories),
        "match_percent": item.match_percent,
        "category_score": item.category_score,
        "final_score": item.final_score,
        "ai_score": item.ai_score,
        "summary": item.summary,
        "suggestions": json.loads(item.suggestions),
        "created_at": item.created_at
    }


@app.get("/results/{analysis_id}/pdf")
def export_result_pdf(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    item = db.query(Analysis).filter(Analysis.id == analysis_id).first()

    if not item:
        return {"error": "Analysis not found"}

    data = {
        "filename": item.filename,
        "provider": item.provider,
        "resume_skills": json.loads(item.resume_skills),
        "job_skills": json.loads(item.job_skills),
        "matched_skills": json.loads(item.matched_skills),
        "missing_skills": json.loads(item.missing_skills),
        "matched_categories": json.loads(item.matched_categories),
        "match_percent": item.match_percent,
        "category_score": item.category_score,
        "final_score": item.final_score,
        "ai_score": item.ai_score,
        "summary": item.summary,
        "suggestions": json.loads(item.suggestions),
    }

    pdf_buffer = create_analysis_pdf(data)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=analysis_{analysis_id}.pdf"
        }
    )
