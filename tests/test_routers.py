import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
import io
from app.models.quiz_data import QuizParameters, QuizData, Student
from main import app


client = TestClient(app)


def test_should_return_home_page_given_root_request():
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 200
    assert "Quiz Grades Processor" in response.text


def test_should_return_upload_form_given_upload_page_request():
    # Act
    response = client.get("/upload")
    
    # Assert
    assert response.status_code == 200
    assert "Upload File" in response.text


@patch("app.services.file_service.FileService.read_file")
def test_should_process_file_given_valid_upload(mock_read_file):
    # Arrange
    # Create a mock DataFrame
    mock_df = pd.DataFrame({
        "Team": ["Team A"],
        "Student Name": ["John Doe"],
        "Score": [12.0],
        "1_Response": ["Answer 1"],
        "1_Score": [3.0]
    })
    mock_read_file.return_value = mock_df
    
    # Create a mock file
    file_content = b"dummy content"
    file = io.BytesIO(file_content)
    
    # Act
    response = client.post(
        "/upload",
        files={"file": ("test.xlsx", file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={
            "original_max_score": "15",
            "new_max_score": "10",
            "original_question_value": "3"
        },
        follow_redirects=False
    )
    
    # Assert
    assert response.status_code == 303  # Redirect
    assert response.headers["location"] == "/results"
    mock_read_file.assert_called_once()


def test_should_return_results_page_given_processed_data():
    # Arrange
    # Create a mock QuizData object
    params = QuizParameters(
        original_max_score=15.0,
        new_max_score=10.0,
        original_question_value=3.0
    )
    
    student = Student(
        team="Team A",
        student_name="John Doe",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        student_id="12345",
        original_score=12.0,
        responses={1: "Answer 1", 2: "Answer 2", 3: "Answer 3", 4: "Answer 4", 5: "Answer 5"},
        scores={1: 3.0, 2: 3.0, 3: 3.0, 4: 3.0, 5: 0.0},
        converted_score=8.0
    )
    
    quiz_data = QuizData(parameters=params, students=[student])
    
    # Mock the session
    with patch("app.routers.quiz.get_quiz_data_from_session") as mock_get_data:
        mock_get_data.return_value = quiz_data
        
        # Act
        response = client.get("/results")
        
        # Assert
        assert response.status_code == 200
        assert "Results" in response.text
        assert "John Doe" in response.text
        assert "8.0" in response.text  # Converted score