import pandas as pd
from typing import List, Dict, Any, Optional
from app.models.quiz_data import QuizParameters, Student, QuizData


class QuizService:
    """Service for handling quiz data processing and score conversion."""
    
    @staticmethod
    def convert_score(original_score: float, params: QuizParameters) -> float:
        """
        Convert a score from the original scale to the new scale.
        
        Args:
            original_score: The original score to convert
            params: Quiz parameters containing conversion information
            
        Returns:
            The converted score on the new scale
        """
        return original_score * (params.new_max_score / params.original_max_score)
    
    @staticmethod
    def process_dataframe(df: pd.DataFrame, params: QuizParameters) -> QuizData:
        """
        Process a DataFrame containing quiz data and convert scores.
        
        Args:
            df: DataFrame containing quiz data
            params: Quiz parameters containing conversion information
            
        Returns:
            QuizData object containing processed data
        """
        return QuizData.from_dataframe(df, params)
    
    @staticmethod
    def get_question_numbers(df: pd.DataFrame) -> List[int]:
        """
        Extract question numbers from DataFrame columns.
        
        Args:
            df: DataFrame containing quiz data
            
        Returns:
            List of question numbers found in the DataFrame
        """
        question_numbers = set()
        
        for col in df.columns:
            if col.endswith("_Response") or col.endswith("_Score"):
                if col[0].isdigit():
                    try:
                        question_num = int(col.split("_")[0])
                        question_numbers.add(question_num)
                    except ValueError:
                        # Skip columns that don't start with a valid number
                        pass
        
        return sorted(list(question_numbers))
    
    @staticmethod
    def verify_calculation(params: QuizParameters) -> bool:
        """
        Verify that the calculation parameters are valid.
        
        Args:
            params: Quiz parameters to verify
            
        Returns:
            True if the calculation is valid, False otherwise
        """
        # Check if original_max_score is divisible by original_question_value
        if params.original_max_score % params.original_question_value != 0:
            return False
        
        # Check if total_questions * new_question_value equals new_max_score
        total_questions = params.total_questions
        new_question_value = params.new_question_value
        
        # Allow for small floating-point differences
        return abs(total_questions * new_question_value - params.new_max_score) < 1e-10