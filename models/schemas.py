"""
Data models for Placement Readiness Evaluator
Production-ready Pydantic v2 schemas
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime


# =========================
# ENUMS
# =========================

class Branch(str, Enum):
    CSE = "computer_science"
    IT = "information_technology"
    ECE = "electronics"
    EE = "electrical"
    MECH = "mechanical"
    CIVIL = "civil"
    OTHER = "other"


class Year(str, Enum):
    FIRST = "1st"
    SECOND = "2nd"
    THIRD = "3rd"
    FOURTH = "4th"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(str, Enum):
    MCQ = "mcq"
    CODING = "coding"
    DESCRIPTIVE = "descriptive"
    BEHAVIORAL = "behavioral"


class SessionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


# =========================
# STUDENT PROFILE
# =========================

class StudentProfile(BaseModel):
    """Student information and background"""

    student_id: str = Field(..., min_length=3, max_length=20)
    name: str
    branch: Branch
    year: Year
    skills: List[str] = Field(default_factory=list)
    target_companies: List[str] = Field(default_factory=list)
    cgpa: Optional[float] = Field(None, ge=0, le=10)
    previous_preparation: Optional[str] = None

    @field_validator("cgpa")
    @classmethod
    def validate_cgpa(cls, v):
        if v is not None and not (0 <= v <= 10):
            raise ValueError("CGPA must be between 0 and 10")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "student_id": "CS2024001",
                "name": "John Doe",
                "branch": "computer_science",
                "year": "3rd",
                "skills": ["Python", "Java", "SQL"],
                "target_companies": ["Google", "Microsoft"],
                "cgpa": 8.5
            }
        }
    )


# =========================
# QUESTION MODEL
# =========================

class Question(BaseModel):
    """Question bank entry"""

    question_id: str
    type: QuestionType
    topic: str
    subtopic: Optional[str] = None
    difficulty: DifficultyLevel
    question_text: str

    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None

    companies_asked: List[str] = Field(default_factory=list)
    time_limit_seconds: Optional[int] = Field(None, gt=0)
    marks: float = Field(default=1.0, gt=0)
    tags: List[str] = Field(default_factory=list)

    @field_validator("options")
    @classmethod
    def validate_options(cls, v, info):
        question_type = info.data.get("type")
        if question_type == QuestionType.MCQ and not v:
            raise ValueError("MCQ questions must include options")
        return v

    @field_validator("correct_answer")
    @classmethod
    def validate_correct_answer(cls, v, info):
        question_type = info.data.get("type")
        if question_type == QuestionType.MCQ and not v:
            raise ValueError("MCQ questions must include a correct_answer")
        return v


# =========================
# RESPONSE MODELS
# =========================

class StudentResponse(BaseModel):
    """Individual response to a question"""

    question_id: str
    student_id: str

    response_text: Optional[str] = None
    selected_option: Optional[str] = None
    code_submission: Optional[str] = None

    time_taken_seconds: int = Field(..., ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EvaluatedResponse(StudentResponse):
    """Response with evaluation"""

    score: float = Field(..., ge=0, le=1)
    feedback: str
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    rubric_scores: Dict[str, float] = Field(default_factory=dict)


# =========================
# ASSESSMENT SESSION
# =========================

class AssessmentSession(BaseModel):
    """Complete assessment session"""

    session_id: str
    student: StudentProfile

    start_time: datetime
    end_time: Optional[datetime] = None
    status: SessionStatus = SessionStatus.IN_PROGRESS

    responses: List[EvaluatedResponse] = Field(default_factory=list)
    current_difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    topics_covered: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =========================
# COMPETENCY SCORES
# =========================

class CompetencyScores(BaseModel):
    """Scores across different areas"""

    aptitude: float = Field(..., ge=0, le=100)
    technical: float = Field(..., ge=0, le=100)
    communication: float = Field(..., ge=0, le=100)
    domain_knowledge: float = Field(..., ge=0, le=100)

    @property
    def overall(self) -> float:
        """Auto-calculate overall score"""
        return round(
            (
                self.aptitude
                + self.technical
                + self.communication
                + self.domain_knowledge
            ) / 4,
            2,
        )

    def to_radar_data(self) -> Dict[str, float]:
        """Convert to format suitable for radar chart"""
        return {
            "Aptitude": self.aptitude,
            "Technical": self.technical,
            "Communication": self.communication,
            "Domain": self.domain_knowledge,
        }


# =========================
# FINAL REPORT
# =========================

class PlacementReadinessReport(BaseModel):
    """Complete assessment report"""

    report_id: str
    session_id: str
    student: StudentProfile
    generated_date: datetime = Field(default_factory=datetime.utcnow)

    competency_scores: CompetencyScores

    topic_wise_scores: Dict[str, float]
    company_fit_scores: Dict[str, float]

    weak_areas: List[str]
    strong_areas: List[str]
    recommendations: List[str]
    resources: List[Dict[str, str]]
    thirty_day_roadmap: List[Dict[str, str]]

    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "report_id": "REP001",
                "session_id": "SESSION001",
                "competency_scores": {
                    "aptitude": 75,
                    "technical": 82,
                    "communication": 68,
                    "domain_knowledge": 70,
                }
            }
        }
    )