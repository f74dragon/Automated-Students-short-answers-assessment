from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class EvaluationBase(BaseModel):
    prompt_id: int
    model_id: int
    question_id: Optional[int] = None
    student_answer_id: Optional[int] = None
    prompt_template: Optional[str] = None
    model_name: Optional[str] = None
    metrics: Dict[str, Any]


class EvaluationCreate(EvaluationBase):
    pass


class EvaluationUpdate(BaseModel):
    metrics: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class Evaluation(EvaluationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class CombinationBase(BaseModel):
    prompt_id: int
    model_id: int
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class CombinationCreate(CombinationBase):
    pass


class CombinationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class Combination(CombinationBase):
    id: int
    is_active: bool = False
    prompt_template: Optional[str] = None
    model_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    average_accuracy: Optional[float] = None
    average_response_time: Optional[float] = None
    consistency_score: Optional[float] = None

    class Config:
        orm_mode = True


class CombinationWithEvaluations(Combination):
    evaluations: List[Evaluation] = []


class CsvQuestion(BaseModel):
    """A question from a CSV file with associated model and student answers."""
    id: int  # Temporary ID for frontend tracking
    text: str
    model_answer: str
    student_answer: str
    reference_grade: Optional[float] = None


class EvaluationRequest(BaseModel):
    """Request for evaluating a model and prompt combination on questions."""
    prompt_id: Optional[int] = None
    model_id: Optional[int] = None
    prompt_template: Optional[str] = None
    model_name: Optional[str] = None
    question_ids: Optional[List[int]] = None
    csv_questions: Optional[List[Dict[str, Any]]] = None
    is_csv: bool = False
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    save_result: bool = True
    combination_name: Optional[str] = None


class EvaluationResult(BaseModel):
    """A simplified evaluation result for API responses."""
    question_id: Optional[int] = None
    prompt: Optional[str] = None
    response: Optional[str] = None
    extracted_grade: Optional[float] = None
    confidence: Optional[str] = None
    response_time: Optional[float] = None
    error: bool = False
    error_message: Optional[str] = None
    reference_grade: Optional[float] = None
    accuracy: Optional[float] = None
    student_answer: Optional[str] = None

class EvaluationResponse(BaseModel):
    combination_id: Optional[int] = None
    model_name: str
    prompt_template: str
    evaluations: List[EvaluationResult] = []
    metrics: Dict[str, Any]
