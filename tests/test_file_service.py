"""
Tests for file service.
"""
import pytest
import pandas as pd
import io
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
from fastapi import UploadFile

from app.services.file_service import save_upload_file_temp, process_file, process_dataframe
from app.models.quiz_data import StudentResponse


@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing."""
    data = {
        'Team': ['Team A', 'Team B'],
        'Student Name': ['John Doe', 'Jane Smith'],
        'First Name': ['John', 'Jane'],
        'Last Name': ['Doe', 'Smith'],
        'Email Address': ['john@example.com', 'jane@example.com'],
        'Student ID': [12345, 67890],
        'Score': [12, 9],
        '1_Response': ['Answer 1.1', 'Answer 1.2'],
        '1_Score': [3, 3],
        '2_Response': ['Answer 2.1', 'Answer 2.2'],
        '2_Score': [3, 0],
        '3_Response': ['Answer 3.1', 'Answer 3.2'],
        '3_Score': [3, 3],
        '4_Response': ['Answer 4.1', 'Answer 4.2'],
        '4_Score': [3, 3],
        '5_Response': ['Answer 5.1', 'Answer 5.2'],
        '5_Score': [0, 0]
    }
    return pd.DataFrame(data)


def test_should_process_dataframe_given_valid_dataframe(sample_dataframe):
    """Test that dataframe is processed correctly."""
    # Arrange
    df = sample_dataframe

    # Act
    student_responses, question_numbers = process_dataframe(df)

    # Assert
    assert len(student_responses) == 2
    assert len(question_numbers) == 5
    assert question_numbers == [1, 2, 3, 4, 5]

    # Check first student
    student1 = student_responses[0]
    assert student1.team == "Team A"
    assert student1.student_name == "John Doe"
    assert student1.first_name == "John"
    assert student1.last_name == "Doe"
    assert student1.email == "john@example.com"
    assert student1.student_id == "12345"
    assert student1.original_score == 12
    assert student1.responses[1] == "Answer 1.1"
    assert student1.question_scores[1] == 3

    # Check second student
    student2 = student_responses[1]
    assert student2.team == "Team B"
    assert student2.student_name == "Jane Smith"
    assert student2.first_name == "Jane"
    assert student2.last_name == "Smith"
    assert student2.email == "jane@example.com"
    assert student2.student_id == "67890"
    assert student2.original_score == 9
    assert student2.responses[2] == "Answer 2.2"
    assert student2.question_scores[2] == 0


@pytest.mark.asyncio
async def test_should_save_upload_file_temp_given_valid_file():
    """Test that uploaded file is saved temporarily."""
    # Arrange
    mock_content = b"test file content"
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "test.xlsx"
    mock_file.read.return_value = mock_content

    # Mock the tempfile.NamedTemporaryFile context manager
    mock_temp_file = MagicMock()
    mock_temp_file.name = "/tmp/test_temp_file.xlsx"

    # Act
    with patch("tempfile.NamedTemporaryFile", return_value=mock_temp_file):
        result = await save_upload_file_temp(mock_file)

    # Assert
    assert isinstance(result, Path)
    assert str(result) == "/tmp/test_temp_file.xlsx"
    mock_file.read.assert_called_once()
    mock_temp_file.write.assert_called_once_with(mock_content)


@pytest.mark.asyncio
async def test_should_process_excel_file_given_valid_upload():
    """Test that Excel file is processed correctly."""
    # Arrange
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "test.xlsx"

    # Mock the save_upload_file_temp function
    mock_temp_path = Path("/tmp/test_temp_file.xlsx")

    # Create a sample dataframe
    df = pd.DataFrame({
        'Team': ['Team A'],
        'Student Name': ['John Doe'],
        'First Name': ['John'],
        'Last Name': ['Doe'],
        'Email Address': ['john@example.com'],
        'Student ID': [12345],
        'Score': [12],
        '1_Response': ['Answer 1'],
        '1_Score': [3]
    })

    # Act
    with patch("app.services.file_service.save_upload_file_temp", return_value=mock_temp_path), \
         patch("pandas.read_excel", return_value=df), \
         patch("os.unlink") as mock_unlink:
        student_responses, question_numbers = await process_file(mock_file)

    # Assert
    assert len(student_responses) == 1
    assert len(question_numbers) == 1
    assert question_numbers == [1]

    student = student_responses[0]
    assert student.team == "Team A"
    assert student.student_name == "John Doe"
    assert student.original_score == 12
    assert student.responses[1] == "Answer 1"
    assert student.question_scores[1] == 3

    # Check that the temp file was deleted
    mock_unlink.assert_called_once_with(mock_temp_path)


@pytest.mark.asyncio
async def test_should_process_excel_file_with_student_analysis_sheet():
    """Test that Excel file with Student Analysis sheet is processed correctly."""
    # Arrange
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "test.xlsx"

    # Mock the save_upload_file_temp function
    mock_temp_path = Path("/tmp/test_temp_file.xlsx")

    # Create a sample dataframe
    df = pd.DataFrame({
        'Team': ['Team A'],
        'Student Name': ['John Doe'],
        'First Name': ['John'],
        'Last Name': ['Doe'],
        'Email Address': ['john@example.com'],
        'Student ID': [12345],
        'Score': [12],
        '1_Response': ['Answer 1'],
        '1_Score': [3]
    })

    # Mock pandas.read_excel to raise ValueError for Team Analysis sheet
    # but return df for Student Analysis sheet
    def mock_read_excel(path, sheet_name=None):
        if sheet_name == "Team Analysis":
            raise ValueError("Worksheet named 'Team Analysis' not found")
        elif sheet_name == "Student Analysis":
            return df
        else:
            return df

    # Act
    with patch("app.services.file_service.save_upload_file_temp", return_value=mock_temp_path), \
         patch("pandas.read_excel", side_effect=mock_read_excel), \
         patch("os.unlink") as mock_unlink:
        student_responses, question_numbers = await process_file(mock_file)

    # Assert
    assert len(student_responses) == 1
    assert len(question_numbers) == 1
    assert question_numbers == [1]

    student = student_responses[0]
    assert student.team == "Team A"
    assert student.student_name == "John Doe"
    assert student.original_score == 12
    assert student.responses[1] == "Answer 1"
    assert student.question_scores[1] == 3

    # Check that the temp file was deleted
    mock_unlink.assert_called_once_with(mock_temp_path)


@pytest.mark.asyncio
async def test_should_process_csv_file_given_valid_upload():
    """Test that CSV file is processed correctly."""
    # Arrange
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "test.csv"

    # Mock the save_upload_file_temp function
    mock_temp_path = Path("/tmp/test_temp_file.csv")

    # Create a sample dataframe
    df = pd.DataFrame({
        'Team': ['Team A'],
        'Student Name': ['John Doe'],
        'First Name': ['John'],
        'Last Name': ['Doe'],
        'Email Address': ['john@example.com'],
        'Student ID': [12345],
        'Score': [12],
        '1_Response': ['Answer 1'],
        '1_Score': [3]
    })

    # Act
    with patch("app.services.file_service.save_upload_file_temp", return_value=mock_temp_path), \
         patch("pandas.read_csv", return_value=df), \
         patch("os.unlink") as mock_unlink:
        student_responses, question_numbers = await process_file(mock_file)

    # Assert
    assert len(student_responses) == 1
    assert len(question_numbers) == 1

    # Check that the temp file was deleted
    mock_unlink.assert_called_once_with(mock_temp_path)


@pytest.mark.asyncio
async def test_should_raise_error_given_unsupported_file_format():
    """Test that an error is raised for unsupported file formats."""
    # Arrange
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "test.txt"

    # Mock the save_upload_file_temp function
    mock_temp_path = Path("/tmp/test_temp_file.txt")

    # Act & Assert
    with patch("app.services.file_service.save_upload_file_temp", return_value=mock_temp_path), \
         patch("os.unlink") as mock_unlink, \
         pytest.raises(ValueError, match="Unsupported file format"):
        await process_file(mock_file)

    # Check that the temp file was deleted even if an error occurred
    mock_unlink.assert_called_once_with(mock_temp_path)
