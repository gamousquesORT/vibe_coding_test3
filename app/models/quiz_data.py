from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Any
import pandas as pd


class Student(BaseModel):
    """Model representing a student's information and quiz results."""
    team: Optional[str] = None
    student_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    student_id: Optional[str] = None
    original_score: float
    responses: Dict[int, Any] = {}  # Question number -> Response
    scores: Dict[int, float] = {}   # Question number -> Score
    converted_score: Optional[float] = None


class QuizParameters(BaseModel):
    """Model representing the parameters for quiz score conversion."""
    original_max_score: float = Field(..., gt=0)
    new_max_score: float = Field(..., gt=0)
    original_question_value: float = Field(..., gt=0)
    
    @property
    def total_questions(self) -> float:
        """Calculate the total number of questions in the quiz."""
        return self.original_max_score / self.original_question_value
    
    @property
    def new_question_value(self) -> float:
        """Calculate the new value per question."""
        return self.new_max_score / self.total_questions


class QuizData(BaseModel):
    """Model representing the processed quiz data."""
    parameters: QuizParameters
    students: List[Student] = []
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, parameters: QuizParameters) -> "QuizData":
        """Create a QuizData instance from a pandas DataFrame."""
        quiz_data = cls(parameters=parameters)
        
        # Process each row (student) in the dataframe
        for _, row in df.iterrows():
            student = Student(
                team=row.get("Team"),
                student_name=row.get("Student Name"),
                first_name=row.get("First Name"),
                last_name=row.get("Last Name"),
                email=row.get("Email Address"),
                student_id=row.get("Student ID"),
                original_score=float(row.get("Score", 0))
            )
            
            # Process question responses and scores
            for col in df.columns:
                if col.endswith("_Response") and col[0].isdigit():
                    question_num = int(col.split("_")[0])
                    student.responses[question_num] = row.get(col)
                
                if col.endswith("_Score") and col[0].isdigit():
                    question_num = int(col.split("_")[0])
                    student.scores[question_num] = float(row.get(col, 0))
            
            # Calculate converted score
            student.converted_score = student.original_score * (parameters.new_max_score / parameters.original_max_score)
            
            quiz_data.students.append(student)
        
        return quiz_data