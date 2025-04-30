"""
File service for handling file uploads and processing.
"""
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
from fastapi import UploadFile
import os
import tempfile
from pathlib import Path

from app.models.quiz_data import StudentResponse


async def save_upload_file_temp(upload_file: UploadFile) -> Path:
    """
    Save an upload file temporarily and return the path.

    Args:
        upload_file: The uploaded file

    Returns:
        Path to the temporary file
    """
    try:
        suffix = Path(upload_file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            content = await upload_file.read()
            temp.write(content)
            temp_path = Path(temp.name)
        return temp_path
    except Exception:
        raise Exception("Failed to save file")


async def process_file(file: UploadFile) -> Tuple[List[StudentResponse], List[int]]:
    """
    Process the uploaded Excel/CSV file and extract student responses.

    Args:
        file: The uploaded file

    Returns:
        Tuple containing list of student responses and list of question numbers
    """
    temp_file = await save_upload_file_temp(file)
    try:
        # Determine file type and read accordingly
        if temp_file.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(temp_file)
        elif temp_file.suffix.lower() == '.csv':
            df = pd.read_csv(temp_file)
        else:
            raise ValueError("Unsupported file format. Please upload an Excel or CSV file.")

        # Process the dataframe
        return process_dataframe(df)
    finally:
        # Clean up the temp file
        os.unlink(temp_file)


def process_dataframe(df: pd.DataFrame) -> Tuple[List[StudentResponse], List[int]]:
    """
    Process the dataframe and extract student responses.

    Args:
        df: Pandas DataFrame containing quiz data

    Returns:
        Tuple containing list of student responses and list of question numbers
    """
    # Debug: Print dataframe columns
    print("DataFrame columns:", df.columns.tolist())

    # Debug: Print first few rows of dataframe
    print("DataFrame head:")
    print(df.head())

    # Identify question columns
    question_columns = [col for col in df.columns if col.endswith('_Response')]
    question_numbers = [int(col.split('_')[0]) for col in question_columns]

    # Debug: Print question columns and numbers
    print("Question columns:", question_columns)
    print("Question numbers:", question_numbers)

    # Identify score columns
    score_columns = [f"{num}_Score" for num in question_numbers]

    # Debug: Print score columns
    print("Score columns:", score_columns)

    # Check if all required columns exist
    required_columns = ['Team', 'Student Name', 'First Name', 'Last Name', 
                        'Email Address', 'Student ID', 'Score']

    # Filter out columns that don't exist in the dataframe
    existing_required_columns = [col for col in required_columns if col in df.columns]

    # Debug: Print existing required columns
    print("Existing required columns:", existing_required_columns)

    # Create student responses
    student_responses = []

    for _, row in df.iterrows():
        # Create a student response object
        student_response = StudentResponse(
            team=row.get('Team') if 'Team' in df.columns else None,
            student_name=row.get('Student Name', ''),
            first_name=row.get('First Name', ''),
            last_name=row.get('Last Name', ''),
            email=row.get('Email Address') if 'Email Address' in df.columns else None,
            student_id=str(row.get('Student ID', '')),
            original_score=float(row.get('Score', 0)),
            responses={},
            question_scores={}
        )

        # Add responses and scores for each question
        for q_num, q_col in zip(question_numbers, question_columns):
            if q_col in df.columns:
                student_response.responses[q_num] = str(row.get(q_col, ''))

            score_col = f"{q_num}_Score"
            if score_col in df.columns:
                student_response.question_scores[q_num] = float(row.get(score_col, 0))

        student_responses.append(student_response)

    return student_responses, question_numbers
