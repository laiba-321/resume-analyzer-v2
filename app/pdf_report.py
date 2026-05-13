from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO


def create_analysis_pdf(data: dict) -> BytesIO:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    y = height - 50

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "AI Resume Analysis Report")

    y -= 40
    pdf.setFont("Helvetica", 11)

    def line(text):
        nonlocal y
        if y < 60:
            pdf.showPage()
            pdf.setFont("Helvetica", 11)
            y = height - 50
        pdf.drawString(50, y, str(text)[:100])
        y -= 22

    line(f"Filename: {data.get('filename')}")
    line(f"Provider: {data.get('provider')}")
    line(f"Final Score: {data.get('final_score')}/100")
    line(f"Keyword Match: {data.get('match_percent')}%")
    line(f"Category Score: {data.get('category_score')}%")
    line(f"AI Score: {data.get('ai_score')}/100")

    y -= 10
    pdf.setFont("Helvetica-Bold", 14)
    line("Summary")
    pdf.setFont("Helvetica", 11)
    line(data.get("summary", ""))

    y -= 10
    pdf.setFont("Helvetica-Bold", 14)
    line("Matched Skills")
    pdf.setFont("Helvetica", 11)
    line(", ".join(data.get("matched_skills", [])))

    y -= 10
    pdf.setFont("Helvetica-Bold", 14)
    line("Missing Skills")
    pdf.setFont("Helvetica", 11)
    line(", ".join(data.get("missing_skills", [])))

    y -= 10
    pdf.setFont("Helvetica-Bold", 14)
    line("Suggestions")
    pdf.setFont("Helvetica", 11)

    for suggestion in data.get("suggestions", []):
        line(f"- {suggestion}")

    pdf.save()
    buffer.seek(0)
    return buffer