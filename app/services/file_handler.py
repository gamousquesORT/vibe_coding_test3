"""
File handler for importing and exporting quiz data.
"""
import os
import pandas as pd
import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple

from app.models.quiz_data import QuizParameters, StudentResponse


class FileHandler:
    """Class for handling file import and export operations."""

    @staticmethod
    def process_file(file_path: str) -> tuple:
        """
        Process the Excel/CSV file and extract student responses.

        Args:
            file_path: Path to the file

        Returns:
            Tuple containing list of student responses and list of question numbers
        """
        try:
            # Check if file exists
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Determine file type and read accordingly
            if file_path.suffix.lower() in ['.xlsx', '.xls']:
                try:
                    # Try to read from the "Team Analysis" sheet
                    df = pd.read_excel(file_path, sheet_name="Team Analysis")
                    print("Reading data from 'Team Analysis' sheet...")
                except ValueError as e:
                    # If the Team Analysis sheet doesn't exist, try Student Analysis sheet
                    if "Worksheet named 'Team Analysis' not found" in str(e):
                        try:
                            # Try to read from the "Student Analysis" sheet
                            df = pd.read_excel(file_path, sheet_name="Student Analysis")
                            print("Reading data from 'Student Analysis' sheet...")
                        except ValueError as e2:
                            # If neither sheet exists, inform the user and raise an error
                            if "Worksheet named 'Student Analysis' not found" in str(e2):
                                raise ValueError("Neither 'Team Analysis' nor 'Student Analysis' sheets were found in the Excel file.")
                            else:
                                raise e2
                    else:
                        raise
            elif file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}. Please provide an Excel (.xlsx, .xls) or CSV (.csv) file.")

            # Check if dataframe is empty
            if df.empty:
                raise ValueError("The file contains no data.")

            # Process the dataframe
            return FileHandler.process_dataframe(df)

        except pd.errors.EmptyDataError:
            raise ValueError("The file contains no data.")
        except pd.errors.ParserError:
            raise ValueError("Error parsing the file. Please check the file format.")
        except Exception as e:
            # Re-raise with more context if it's not already a custom error
            if not isinstance(e, (ValueError, FileNotFoundError)):
                raise ValueError(f"Error processing file: {str(e)}")
            raise

    @staticmethod
    def process_dataframe(df: pd.DataFrame) -> tuple:
        """
        Process the dataframe and extract student responses.

        Args:
            df: Pandas DataFrame containing quiz data

        Returns:
            Tuple containing list of student responses and list of question numbers
        """
        try:
            # Check for required columns
            required_columns = ['Student Name', 'First Name', 'Last Name', 'Student ID', 'Score']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

            # Identify question columns
            question_columns = [col for col in df.columns if col.endswith('_Response')]
            if not question_columns:
                raise ValueError("No question response columns found. Column names should end with '_Response'.")

            # Extract question numbers, handling potential format issues
            question_numbers = []
            for col in question_columns:
                try:
                    # Extract the part before '_Response' and convert to int
                    q_num = int(col.split('_')[0])
                    question_numbers.append(q_num)
                except (ValueError, IndexError):
                    # Skip columns with invalid format
                    print(f"Warning: Skipping column '{col}' - could not extract question number.")
                    continue

            if not question_numbers:
                raise ValueError("No valid question numbers found in column names.")

            # Identify score columns
            score_columns = [f"{num}_Score" for num in question_numbers]

            # Create student responses
            student_responses = []

            for idx, row in df.iterrows():
                try:
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
                            try:
                                student_response.question_scores[q_num] = float(row.get(score_col, 0))
                            except (ValueError, TypeError):
                                print(f"Warning: Invalid score value for student {student_response.student_name}, question {q_num}. Using 0.")
                                student_response.question_scores[q_num] = 0.0

                    student_responses.append(student_response)

                except Exception as e:
                    print(f"Warning: Error processing row {idx+1}: {str(e)}. Skipping this student.")
                    continue

            if not student_responses:
                raise ValueError("No valid student responses could be processed from the file.")

            return student_responses, question_numbers

        except Exception as e:
            # If it's not already a ValueError, wrap it
            if not isinstance(e, ValueError):
                raise ValueError(f"Error processing data: {str(e)}")
            raise

    @staticmethod
    def get_output_folder() -> str:
        """
        Ask the user for the output folder and validate it.

        Returns:
            Path to the output folder
        """
        while True:
            folder_path = input("\nOutput folder path (leave empty for current directory): ").strip()

            # Use current directory if empty
            if not folder_path:
                return ""

            # Check if the path exists and is a directory
            path = Path(folder_path)
            if not path.exists():
                create = input(f"Folder '{folder_path}' does not exist. Create it? (y/n): ").lower()
                if create == 'y':
                    try:
                        path.mkdir(parents=True, exist_ok=True)
                        print(f"Folder '{folder_path}' created successfully.")
                        return folder_path
                    except Exception as e:
                        print(f"Error creating folder: {str(e)}")
                        continue
                else:
                    continue
            elif not path.is_dir():
                print(f"Error: '{folder_path}' is not a directory.")
                continue

            # Check if the directory is writable
            try:
                # Try to create a temporary file to check if the directory is writable
                temp_file = path / ".write_test"
                temp_file.touch()
                temp_file.unlink()  # Remove the test file
                return folder_path
            except Exception:
                print(f"Error: Cannot write to '{folder_path}'. Please check permissions.")
                continue

    @staticmethod
    def export_to_excel(quiz_params: QuizParameters, output_data: List[Dict[str, Any]], 
                        question_numbers: List[int], output_folder: str = ""):
        """
        Export the results to an Excel file.

        Args:
            quiz_params: Quiz parameters
            output_data: List of dictionaries with formatted output data
            question_numbers: List of question numbers
            output_folder: Folder where to save the file (default: current directory)
        """
        filename = f"{quiz_params.quiz_name}.xlsx"

        # Combine output folder with filename if provided
        if output_folder:
            file_path = Path(output_folder) / filename
        else:
            file_path = Path(filename)

        # Convert the output data to a pandas DataFrame
        df = pd.DataFrame(output_data)

        # Export to Excel
        df.to_excel(file_path, index=False)

        print(f"\nResults exported to {file_path}")

    @staticmethod
    def export_to_csv(quiz_params: QuizParameters, output_data: List[Dict[str, Any]], 
                      question_numbers: List[int], output_folder: str = ""):
        """
        Export the results to a CSV file.

        Args:
            quiz_params: Quiz parameters
            output_data: List of dictionaries with formatted output data
            question_numbers: List of question numbers
            output_folder: Folder where to save the file (default: current directory)
        """
        filename = f"{quiz_params.quiz_name}.csv"

        # Combine output folder with filename if provided
        if output_folder:
            file_path = Path(output_folder) / filename
        else:
            file_path = Path(filename)

        with open(file_path, 'w', newline='') as csvfile:
            # Determine all possible fields
            fieldnames = ['Team', 'Student Name', 'First Name', 'Last Name', 'Student ID', 'Original Score', 'Converted Score']
            for q_num in question_numbers:
                fieldnames.extend([f"Q{q_num} Response", f"Q{q_num} Original Score", f"Q{q_num} Converted Score"])

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for student in output_data:
                writer.writerow(student)

        print(f"\nResults exported to {file_path}")
