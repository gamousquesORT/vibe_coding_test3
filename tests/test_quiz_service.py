import pytest
import pandas as pd
from app.models.quiz_data import QuizParameters, Student, QuizData
from app.services.quiz_service import QuizService


def test_should_convert_scores_given_quiz_parameters():
    # Arrange
    params = QuizParameters(
        original_max_score=15.0,
        new_max_score=10.0,
        original_question_value=3.0
    )
    
    # Create a sample student
    student = Student(
        team="Team A",
        student_name="John Doe",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        student_id="12345",
        original_score=12.0,
        responses={1: "Answer 1", 2: "Answer 2", 3: "Answer 3", 4: "Answer 4", 5: "Answer 5"},
        scores={1: 3.0, 2: 3.0, 3: 3.0, 4: 3.0, 5: 0.0}
    )
    
    # Act
    converted_score = QuizService.convert_score(student.original_score, params)
    
    # Assert
    assert converted_score == 8.0  # 12 * (10/15) = 8


def test_should_process_dataframe_given_quiz_parameters():
    # Arrange
    params = QuizParameters(
        original_max_score=15.0,
        new_max_score=10.0,
        original_question_value=3.0
    )
    
    # Create a sample DataFrame
    data = {
        "Team": ["Team A", "Team B"],
        "Student Name": ["John Doe", "Jane Smith"],
        "First Name": ["John", "Jane"],
        "Last Name": ["Doe", "Smith"],
        "Email Address": ["john.doe@example.com", "jane.smith@example.com"],
        "Student ID": ["12345", "67890"],
        "Score": [12.0, 9.0],
        "1_Response": ["Answer 1", "Answer 1"],
        "1_Score": [3.0, 3.0],
        "2_Response": ["Answer 2", "Answer 2"],
        "2_Score": [3.0, 3.0],
        "3_Response": ["Answer 3", "Answer 3"],
        "3_Score": [3.0, 3.0],
        "4_Response": ["Answer 4", "Wrong"],
        "4_Score": [3.0, 0.0],
        "5_Response": ["Answer 5", "Wrong"],
        "5_Score": [0.0, 0.0]
    }
    df = pd.DataFrame(data)
    
    # Act
    quiz_data = QuizService.process_dataframe(df, params)
    
    # Assert
    assert isinstance(quiz_data, QuizData)
    assert len(quiz_data.students) == 2
    assert quiz_data.students[0].converted_score == 8.0  # 12 * (10/15) = 8
    assert quiz_data.students[1].converted_score == 6.0  # 9 * (10/15) = 6
    assert quiz_data.parameters.total_questions == 5.0
    assert quiz_data.parameters.new_question_value == 2.0


def test_should_get_question_numbers_given_dataframe():
    # Arrange
    # Create a sample DataFrame
    data = {
        "Team": ["Team A"],
        "Student Name": ["John Doe"],
        "Score": [12.0],
        "1_Response": ["Answer 1"],
        "1_Score": [3.0],
        "2_Response": ["Answer 2"],
        "2_Score": [3.0],
        "3_Response": ["Answer 3"],
        "3_Score": [3.0],
        "4_Response": ["Answer 4"],
        "4_Score": [3.0],
        "5_Response": ["Answer 5"],
        "5_Score": [0.0]
    }
    df = pd.DataFrame(data)
    
    # Act
    question_numbers = QuizService.get_question_numbers(df)
    
    # Assert
    assert question_numbers == [1, 2, 3, 4, 5]


def test_should_verify_calculation_given_quiz_parameters():
    # Arrange
    params = QuizParameters(
        original_max_score=15.0,
        new_max_score=10.0,
        original_question_value=3.0
    )
    
    # Act
    is_valid = QuizService.verify_calculation(params)
    
    # Assert
    assert is_valid is True
    
    # Test with invalid parameters
    invalid_params = QuizParameters(
        original_max_score=16.0,  # Not divisible by original_question_value
        new_max_score=10.0,
        original_question_value=3.0
    )
    
    # Act & Assert
    assert QuizService.verify_calculation(invalid_params) is False