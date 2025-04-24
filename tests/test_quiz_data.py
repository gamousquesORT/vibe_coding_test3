import pytest
import pandas as pd
from app.models.quiz_data import Student, QuizParameters, QuizData


def test_should_calculate_total_questions_given_quiz_parameters():
    # Arrange
    params = QuizParameters(
        original_max_score=15.0,
        new_max_score=10.0,
        original_question_value=3.0
    )
    
    # Act
    total_questions = params.total_questions
    
    # Assert
    assert total_questions == 5.0


def test_should_calculate_new_question_value_given_quiz_parameters():
    # Arrange
    params = QuizParameters(
        original_max_score=15.0,
        new_max_score=10.0,
        original_question_value=3.0
    )
    
    # Act
    new_question_value = params.new_question_value
    
    # Assert
    assert new_question_value == 2.0


def test_should_convert_student_score_given_quiz_parameters():
    # Arrange
    params = QuizParameters(
        original_max_score=15.0,
        new_max_score=10.0,
        original_question_value=3.0
    )
    
    # Create a sample DataFrame
    data = {
        "Team": ["Team A"],
        "Student Name": ["John Doe"],
        "First Name": ["John"],
        "Last Name": ["Doe"],
        "Email Address": ["john.doe@example.com"],
        "Student ID": ["12345"],
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
    quiz_data = QuizData.from_dataframe(df, params)
    
    # Assert
    assert len(quiz_data.students) == 1
    student = quiz_data.students[0]
    assert student.team == "Team A"
    assert student.student_name == "John Doe"
    assert student.original_score == 12.0
    assert student.converted_score == 8.0  # 12 * (10/15) = 8
    assert len(student.responses) == 5
    assert len(student.scores) == 5
    assert student.scores[1] == 3.0
    assert student.scores[5] == 0.0
    assert student.responses[1] == "Answer 1"


def test_should_handle_missing_values_given_incomplete_data():
    # Arrange
    params = QuizParameters(
        original_max_score=15.0,
        new_max_score=10.0,
        original_question_value=3.0
    )
    
    # Create a sample DataFrame with missing values
    data = {
        "Score": [9.0],
        "1_Response": ["Answer 1"],
        "1_Score": [3.0],
        "2_Response": ["Answer 2"],
        "2_Score": [3.0],
        "3_Response": ["Answer 3"],
        "3_Score": [3.0]
    }
    df = pd.DataFrame(data)
    
    # Act
    quiz_data = QuizData.from_dataframe(df, params)
    
    # Assert
    assert len(quiz_data.students) == 1
    student = quiz_data.students[0]
    assert student.team is None
    assert student.student_name is None
    assert student.original_score == 9.0
    assert student.converted_score == 6.0  # 9 * (10/15) = 6
    assert len(student.responses) == 3
    assert len(student.scores) == 3