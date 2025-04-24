import pytest
import pandas as pd
import os
from unittest.mock import patch, mock_open
from app.services.file_service import FileService


def test_should_read_excel_file_given_valid_path():
    # Arrange
    # Create a mock Excel file content
    with patch('pandas.read_excel') as mock_read_excel:
        # Setup the mock to return a predefined DataFrame
        mock_df = pd.DataFrame({
            "Team": ["Team A"],
            "Student Name": ["John Doe"],
            "Score": [12.0],
            "1_Response": ["Answer 1"],
            "1_Score": [3.0]
        })
        mock_read_excel.return_value = mock_df
        
        # Act
        result = FileService.read_file("test.xlsx")
        
        # Assert
        assert isinstance(result, pd.DataFrame)
        assert "Team" in result.columns
        assert "Student Name" in result.columns
        assert "Score" in result.columns
        assert "1_Response" in result.columns
        assert "1_Score" in result.columns
        mock_read_excel.assert_called_once_with("test.xlsx")


def test_should_read_csv_file_given_valid_path():
    # Arrange
    # Create a mock CSV file content
    with patch('pandas.read_csv') as mock_read_csv:
        # Setup the mock to return a predefined DataFrame
        mock_df = pd.DataFrame({
            "Team": ["Team A"],
            "Student Name": ["John Doe"],
            "Score": [12.0],
            "1_Response": ["Answer 1"],
            "1_Score": [3.0]
        })
        mock_read_csv.return_value = mock_df
        
        # Act
        result = FileService.read_file("test.csv")
        
        # Assert
        assert isinstance(result, pd.DataFrame)
        assert "Team" in result.columns
        assert "Student Name" in result.columns
        assert "Score" in result.columns
        assert "1_Response" in result.columns
        assert "1_Score" in result.columns
        mock_read_csv.assert_called_once_with("test.csv")


def test_should_raise_error_given_unsupported_file_extension():
    # Act & Assert
    with pytest.raises(ValueError, match="Unsupported file format"):
        FileService.read_file("test.txt")


def test_should_save_file_given_valid_dataframe_and_path():
    # Arrange
    df = pd.DataFrame({
        "Team": ["Team A"],
        "Student Name": ["John Doe"],
        "Score": [12.0]
    })
    
    # Act & Assert
    with patch('pandas.DataFrame.to_excel') as mock_to_excel:
        FileService.save_file(df, "output.xlsx")
        mock_to_excel.assert_called_once_with("output.xlsx", index=False)
    
    with patch('pandas.DataFrame.to_csv') as mock_to_csv:
        FileService.save_file(df, "output.csv")
        mock_to_csv.assert_called_once_with("output.csv", index=False)
    
    with pytest.raises(ValueError, match="Unsupported file format"):
        FileService.save_file(df, "output.txt")