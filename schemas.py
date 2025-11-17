"""
Database Schemas for International Institute of Languages

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name.

Use these schemas across the app for validation and to power the database viewer.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date


class Course(BaseModel):
    """
    Courses offered by the institute (IELTS, PTE, Foreign Languages, etc.)
    Collection: "course"
    """
    slug: str = Field(..., description="URL-friendly unique identifier (e.g., ielts-coaching)")
    title: str = Field(..., description="Course title")
    category: str = Field(..., description="Category like 'Exam Prep' or 'Foreign Language'")
    short_description: str = Field(..., description="Brief summary for cards")
    description: Optional[str] = Field(None, description="Detailed overview")
    image_url: Optional[str] = Field(None, description="Hero/cover image")
    icon: Optional[str] = Field(None, description="Lucide icon name for UI")
    duration_weeks: Optional[int] = Field(None, ge=1, description="Approximate duration in weeks")
    price: Optional[float] = Field(None, ge=0, description="Indicative price")
    highlights: Optional[List[str]] = Field(default_factory=list, description="Key benefits bullets")
    syllabus: Optional[List[str]] = Field(default_factory=list, description="Syllabus outline bullets")


class Testimonial(BaseModel):
    """
    Student testimonials with outcomes
    Collection: "testimonial"
    """
    name: str
    course_slug: Optional[str] = Field(None, description="Reference to related course")
    message: str
    score_or_result: Optional[str] = Field(None, description="e.g., IELTS 8.0 Overall")
    avatar_url: Optional[str] = None


class BlogPost(BaseModel):
    """
    Blog / Resources articles
    Collection: "blogpost"
    """
    slug: str
    title: str
    excerpt: str
    content: Optional[str] = None
    cover_image_url: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    published_on: Optional[date] = None


class Enquiry(BaseModel):
    """
    Contact / Enquiry submissions
    Collection: "enquiry"
    """
    name: str
    email: EmailStr
    phone: Optional[str] = None
    course_interest: Optional[str] = None
    message: Optional[str] = None


# Optional: Basic institute info for About/SEO (can be extended later)
class InstituteInfo(BaseModel):
    """
    Core institute information for About page and SEO
    Collection: "instituteinfo"
    """
    name: str = Field("International Institute of Languages")
    tagline: Optional[str] = None
    mission: Optional[str] = None
    vision: Optional[str] = None
    address: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    social_links: Optional[dict] = Field(default_factory=dict)
