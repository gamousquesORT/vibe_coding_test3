"""
Tests for quiz data models.
"""
import pytest
from app.models.quiz_data import QuizParameters, StudentResponse, ProcessedResponse


def test_should_calculate_total_questions_given_valid_parameters():
    """Test that total_questions is calculated correctly."""
    # Arrange
    quiz_params = QuizParameters(
        quiz_name="Test Quiz",
        original_max_score=15,
        new_max_score=10,
        original_question_value=3
    )
    
    # Act
    total_questions = quiz_params.total_questions
    
    # Assert
    assert total_questions == 5


def test_should_calculate_new_question_value_given_valid_parameters():
    """Test that new_question_value is calculated correctly."""
    # Arrange
    quiz_params = QuizParameters(
        quiz_name="Test Quiz",
        original_max_score=15,
        new_max_score=10,
        original_question_value=3
    )
    
    # Act
    new_question_value = quiz_params.new_question_value
    
    # Assert
    assert new_question_value == 2


def test_should_verify_calculation_given_valid_parameters():
    """Test that verify_calculation returns True for valid parameters."""
    # Arrange
    quiz_params = QuizParameters(
        quiz_name="Test Quiz",
        original_max_score=15,
        new_max_score=10,
        original_question_value=3
    )
    
    # Act
    result = quiz_params.verify_calculation()
    
    # Assert
    assert result is True


def test_should_verify_calculation_given_invalid_parameters():
    """Test that verify_calculation returns False for invalid parameters."""
    # Arrange
    # This is an invalid setup where the calculation won't verify
    # (15/3) * 9.9 != 10
    quiz_params = QuizParameters(
        quiz_name="Test Quiz",
        original_max_score=15,
        new_max_score=10,
        original_question_value=3
    )
    
    # Manually modify new_max_score to create an invalid state
    # This is just for testing purposes
    quiz_params.new_max_score = 9.9
    
    # Act
    result = quiz_params.verify_calculation()
    
    # Assert
    assert result is False


def test_should_create_student_response_given_valid_data():
    """Test that StudentResponse can be created with valid data."""
    # Arrange & Act
    student = StudentResponse(
        team="Team A",
        student_name="John Doe",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        student_id="12345",
        original_score=12.5,
        responses={1: "Answer 1", 2: "Answer 2"},
        question_scores={1: 2.5, 2: 3.0}
    )
    
    # Assert
    assert student.team == "Team A"
    assert student.student_name == "John Doe"
    assert student.first_name == "John"
    assert student.last_name == "Doe"
    assert student.email == "john.doe@example.com"
    assert student.student_id == "12345"
    assert student.original_score == 12.5
    assert student.responses == {1: "Answer 1", 2: "Answer 2"}
    assert student.question_scores == {1: 2.5, 2: 3.0}


def test_should_create_processed_response_given_valid_data():
    """Test that ProcessedResponse can be created with valid data."""
    # Arrange & Act
    processed = ProcessedResponse(
        team="Team A",
        student_name="John Doe",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        student_id="12345",
        original_score=12.5,
        responses={1: "Answer 1", 2: "Answer 2"},
        question_scores={1: 2.5, 2: 3.0},
        new_score=8.33,
        question_new_scores={1: 1.67, 2: 2.0}
    )
    
    # Assert
    assert processed.team == "Team A"
    assert processed.student_name == "John Doe"
    assert processed.first_name == "John"
    assert processed.last_name == "Doe"
    assert processed.email == "john.doe@example.com"
    assert processed.student_id == "12345"
    assert processed.original_score == 12.5
    assert processed.responses == {1: "Answer 1", 2: "Answer 2"}
    assert processed.question_scores == {1: 2.5, 2: 3.0}
    assert processed.new_score == 8.33
    assert processed.question_new_scores == {1: 1.67, 2: 2.0}