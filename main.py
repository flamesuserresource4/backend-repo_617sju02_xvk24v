import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Course, Testimonial, Enquiry


class ObjectIdEncoder(BaseModel):
    class Config:
        json_encoders = {ObjectId: str}


app = FastAPI(title="International Institute of Languages API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "International Institute of Languages API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            try:
                collections = db.list_collection_names()
                response["collections"] = collections
            except Exception as e:
                response["collections_error"] = str(e)
        else:
            response["database"] = "❌ Not Available"
    except Exception as e:
        response["error"] = str(e)
    return response


# ---------- Seed sample data on first run ----------

def seed_if_empty():
    if db is None:
        return
    # Courses
    if db["course"].count_documents({}) == 0:
        sample_courses: List[Course] = [
            Course(
                slug="ielts-coaching",
                title="IELTS Coaching",
                category="Exam Prep",
                short_description="Master IELTS with expert trainers and personalized feedback.",
                description="A structured IELTS program covering Listening, Reading, Writing, and Speaking with mock tests and band-improvement strategies.",
                image_url="https://images.unsplash.com/photo-1517520287167-4bbf64a00d66?q=80&w=1600&auto=format&fit=crop",
                icon="GraduationCap",
                duration_weeks=8,
                price=299.0,
                highlights=[
                    "Band-focused curriculum",
                    "Weekly mock tests",
                    "Speaking rooms and feedback",
                ],
                syllabus=[
                    "Diagnostic test",
                    "Module-wise mastery",
                    "Full-length mocks",
                ],
            ),
            Course(
                slug="pte-preparation",
                title="PTE Preparation",
                category="Exam Prep",
                short_description="Ace PTE with strategy-driven sessions and practice labs.",
                description="Learn the PTE patterns, time management and scoring mechanics with practice on real-like tests.",
                image_url="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=1600&auto=format&fit=crop",
                icon="BookOpen",
                duration_weeks=6,
                price=249.0,
                highlights=["AI-scored practice", "Templates and hacks", "Doubt-clearing clinics"],
                syllabus=["Speaking & Writing", "Reading", "Listening"],
            ),
            Course(
                slug="foreign-languages",
                title="Foreign Languages",
                category="Language",
                short_description="Learn German, French, Spanish, Japanese and more.",
                description="Level-based language learning with immersive activities and conversation practice.",
                image_url="https://images.unsplash.com/photo-1546410531-bb4caa6b424d?q=80&w=1600&auto=format&fit=crop",
                icon="Globe2",
                duration_weeks=12,
                price=399.0,
                highlights=["A1–C1 levels", "Native mentors", "Cultural immersion"],
                syllabus=["Basics", "Grammar & Vocabulary", "Conversation"],
            ),
        ]
        for c in sample_courses:
            create_document("course", c)

    # Testimonials
    if db["testimonial"].count_documents({}) == 0:
        testimonials = [
            Testimonial(name="Aarav S.", course_slug="ielts-coaching", message="Scored an overall 8.0! The mocks and feedback were game-changers.", score_or_result="IELTS 8.0"),
            Testimonial(name="Meera T.", course_slug="pte-preparation", message="I loved the labs. Cracked PTE in the first attempt.", score_or_result="PTE 79+"),
        ]
        for t in testimonials:
            create_document("testimonial", t)


@app.on_event("startup")
async def on_startup():
    seed_if_empty()


# ---------- API: Courses ----------

@app.get("/api/courses")
def list_courses():
    docs = get_documents("course")
    for d in docs:
        d["_id"] = str(d["_id"]) if "_id" in d else None
    return {"items": docs}


@app.get("/api/courses/{slug}")
def get_course(slug: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    doc = db["course"].find_one({"slug": slug})
    if not doc:
        raise HTTPException(status_code=404, detail="Course not found")
    doc["_id"] = str(doc["_id"]) if "_id" in doc else None
    return doc


# ---------- API: Testimonials ----------

@app.get("/api/testimonials")
def list_testimonials(limit: Optional[int] = 10):
    docs = get_documents("testimonial", {}, limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return {"items": docs}


# ---------- API: Enquiries ----------

@app.post("/api/enquiries")
def submit_enquiry(payload: Enquiry):
    enquiry_id = create_document("enquiry", payload)
    return {"status": "ok", "id": enquiry_id}


# Optional: expose schemas list for admin/viewer tools
@app.get("/schema")
def schema_info():
    return {
        "collections": [
            "course",
            "testimonial",
            "blogpost",
            "enquiry",
            "instituteinfo",
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
