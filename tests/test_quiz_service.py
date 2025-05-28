"""
Tests for quiz service.
"""
import pytest
from app.models.quiz_data import QuizParameters, StudentResponse, ProcessedResponse
from app.services.quiz_service import convert_scores, verify_conversion, generate_output_data


def test_should_convert_scores_given_valid_student_responses_and_quiz_parameters():
    """Test that scores are converted correctly."""
    # Arrange
    quiz_params = QuizParameters(
        quiz_name="Test Quiz",
        original_max_score=15,
        new_max_score=10,
        original_question_value=3
    )
    
    student_responses = [
        StudentResponse(
            team="Team A",
            student_name="John Doe",
            first_name="John",
            last_name="Doe",
            student_id="12345",
            original_score=12,
            question_scores={1: 3, 2: 3, 3: 3, 4: 3, 5: 0}
        ),
        StudentResponse(
            team="Team B",
            student_name="Jane Smith",
            first_name="Jane",
            last_name="Smith",
            student_id="67890",
            original_score=9,
            question_scores={1: 3, 2: 0, 3: 3, 4: 3, 5: 0}
        )
    ]
    
    # Act
    processed_responses = convert_scores(student_responses, quiz_params)
    
    # Assert
    assert len(processed_responses) == 2
    
    # Check first student
    assert processed_responses[0].new_score == 8  # 12 * (10/15) = 8
    assert processed_responses[0].question_new_scores[1] == 2  # 3 * (10/15) = 2
    assert processed_responses[0].question_new_scores[5] == 0  # 0 * (10/15) = 0
    
    # Check second student
    assert processed_responses[1].new_score == 6  # 9 * (10/15) = 6
    assert processed_responses[1].question_new_scores[1] == 2  # 3 * (10/15) = 2
    assert processed_responses[1].question_new_scores[2] == 0  # 0 * (10/15) = 0


def test_should_verify_conversion_given_valid_processed_responses():
    """Test that verification passes for valid processed responses."""
    # Arrange
    processed_responses = [
        ProcessedResponse(
            team="Team A",
            student_name="John Doe",
            first_name="John",
            last_name="Doe",
            student_id="12345",
            original_score=12,
            new_score=8,
            question_scores={1: 3, 2: 3, 3: 3, 4: 3, 5: 0},
            question_new_scores={1: 2, 2: 2, 3: 2, 4: 2, 5: 0}
        ),
        ProcessedResponse(
            team="Team B",
            student_name="Jane Smith",
            first_name="Jane",
            last_name="Smith",
            student_id="67890",
            original_score=9,
            new_score=6,
            question_scores={1: 3, 2: 0, 3: 3, 4: 3, 5: 0},
            question_new_scores={1: 2, 2: 0, 3: 2, 4: 2, 5: 0}
        )
    ]
    
    # Act
    result = verify_conversion(processed_responses)
    
    # Assert
    assert result is True


def test_should_fail_verification_given_invalid_processed_responses():
    """Test that verification fails for invalid processed responses."""
    # Arrange
    processed_responses = [
        ProcessedResponse(
            team="Team A",
            student_name="John Doe",
            first_name="John",
            last_name="Doe",
            student_id="12345",
            original_score=12,
            new_score=8,
            question_scores={1: 3, 2: 3, 3: 3, 4: 3, 5: 0},
            # Incorrect conversion for question 1 (should be 2)
            question_new_scores={1: 1.5, 2: 2, 3: 2, 4: 2, 5: 0}
        )
    ]
    
    # Act
    result = verify_conversion(processed_responses)
    
    # Assert
    assert result is False


def test_should_generate_output_data_given_processed_responses_and_question_numbers():
    """Test that output data is generated correctly."""
    # Arrange
    processed_responses = [
        ProcessedResponse(
            team="Team A",
            student_name="John Doe",
            first_name="John",
            last_name="Doe",
            student_id="12345",
            original_score=12,
            new_score=8,
            responses={1: "Answer 1", 2: "Answer 2"},
            question_scores={1: 3, 2: 3},
            question_new_scores={1: 2, 2: 2}
        )
    ]
    
    question_numbers = [1, 2]
    
    # Act
    output_data = generate_output_data(processed_responses, question_numbers)
    
    # Assert
    assert len(output_data) == 1
    
    student_data = output_data[0]
    assert student_data["Team"] == "Team A"
    assert student_data["Student Name"] == "John Doe"
    assert student_data["First Name"] == "John"
    assert student_data["Last Name"] == "Doe"
    assert student_data["Student ID"] == "12345"
    assert student_data["Original Score"] == 12
    assert student_data["Converted Score"] == 8
    
    assert student_data["Q1 Response"] == "Answer 1"
    assert student_data["Q1 Original Score"] == 3
    assert student_data["Q1 Converted Score"] == 2
    
    assert student_data["Q2 Response"] == "Answer 2"
    assert student_data["Q2 Original Score"] == 3
    assert student_data["Q2 Converted Score"] == 2