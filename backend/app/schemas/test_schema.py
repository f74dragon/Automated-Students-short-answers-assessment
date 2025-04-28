from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class TestConfigBase(BaseModel):
    """Base schema for test configuration."""
    name: str = Field(..., title="Test name", description="Name of the test")
    description: Optional[str] = Field(None, title="Description", description="Description of the test")


class TestCreate(TestConfigBase):
    """Schema for creating a new test."""
    model_names: List[str] = Field(..., title="Model names", description="Names of models to use for testing")
    prompt_ids: List[int] = Field(..., title="Prompt IDs", description="IDs of prompts to use for testing")


class TestUpload(BaseModel):
    """Schema for uploading test data."""
    test_id: int = Field(..., title="Test ID", description="ID of the test to upload data for")
    file_content: str = Field(..., title="File content", description="Content of the uploaded CSV file")


class TestStatus(str):
    """Test status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TestConfig(TestConfigBase):
    """Schema for a test configuration."""
    id: int
    model_names: List[str]
    prompt_ids: List[int]
    status: str = Field(TestStatus.PENDING, title="Status", description="Status of the test")
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TestResultBase(BaseModel):
    """Base schema for test results."""
    test_id: int
    model_name: str
    prompt_id: int
    question: str
    student_answer: str
    model_answer: str
    model_grade: float
    extracted_grade: float
    accuracy: float
    response_time: float
    full_response: str


class TestResultCreate(TestResultBase):
    """Schema for creating a test result."""
    pass


class TestResult(TestResultBase):
    """Schema for a test result."""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class TestSummary(BaseModel):
    """Schema for test summary statistics."""
    test_id: int
    model_name: str
    prompt_id: int
    average_accuracy: float
    average_response_time: float
    total_questions: int

    class Config:
        orm_mode = True


class TestWithResults(TestConfig):
    """Schema for a test with its results."""
    results: List[TestResult] = []
    summaries: List[TestSummary] = []

    class Config:
        orm_mode = True
