import os
import pandas as pd
from pathlib import Path
import csv
import sys
from typing import List, Dict, Any

from app.models.quiz_data import QuizParameters, StudentResponse
from app.services.quiz_service import convert_scores, verify_conversion, generate_output_data

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
                # If the sheet doesn't exist, inform the user and raise an error
                if "Worksheet named 'Team Analysis' not found" in str(e):
                    raise ValueError("The 'Team Analysis' sheet was not found in the Excel file.")
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
        return process_dataframe(df)

    except pd.errors.EmptyDataError:
        raise ValueError("The file contains no data.")
    except pd.errors.ParserError:
        raise ValueError("Error parsing the file. Please check the file format.")
    except Exception as e:
        # Re-raise with more context if it's not already a custom error
        if not isinstance(e, (ValueError, FileNotFoundError)):
            raise ValueError(f"Error processing file: {str(e)}")
        raise

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

def display_results(quiz_params: QuizParameters, output_data: List[Dict[str, Any]], question_numbers: List[int]):
    """
    Display the results in a formatted way.

    Args:
        quiz_params: Quiz parameters
        output_data: List of dictionaries with formatted output data
        question_numbers: List of question numbers
    """
    print("\n" + "="*80)
    print(f"QUIZ RESULTS: {quiz_params.quiz_name}")
    print("="*80)

    print("\nQUIZ PARAMETERS:")
    print(f"Original Maximum Score: {quiz_params.original_max_score}")
    print(f"New Maximum Score: {quiz_params.new_max_score}")
    print(f"Original Question Value: {quiz_params.original_question_value}")
    print(f"Total Questions: {quiz_params.total_questions}")
    print(f"New Question Value: {quiz_params.new_question_value}")

    print("\nVERIFICATION:")
    print(f"Total Questions × New Question Value = New Maximum Score")
    print(f"{quiz_params.total_questions} × {quiz_params.new_question_value} = {quiz_params.total_questions * quiz_params.new_question_value}")

    if quiz_params.verify_calculation():
        print("✓ Calculation verified successfully!")
    else:
        print("✗ Calculation verification failed!")

    print("\nSTUDENT INFORMATION AND TOTAL SCORES:")
    print("-"*80)
    print(f"{'Team':<10} {'Student Name':<20} {'First Name':<15} {'Last Name':<15} {'Student ID':<10} {'Original':<10} {'Converted':<10}")
    print("-"*80)

    for student in output_data:
        print(f"{student['Team']:<10} {student['Student Name']:<20} {student['First Name']:<15} {student['Last Name']:<15} {student['Student ID']:<10} {student['Original Score']:<10} {student['Converted Score']:<10}")

    print("\nQUESTION RESPONSES AND SCORES:")
    print("-"*80)
    header = "Student Name"
    for q_num in question_numbers:
        header += f" | Q{q_num} Resp | Q{q_num} Orig | Q{q_num} Conv"
    print(header)
    print("-"*80)

    for student in output_data:
        row = f"{student['Student Name']:<12}"
        for q_num in question_numbers:
            response = student.get(f"Q{q_num} Response", "")
            orig_score = student.get(f"Q{q_num} Original Score", "")
            conv_score = student.get(f"Q{q_num} Converted Score", "")
            row += f" | {response:<8} | {orig_score:<9} | {conv_score:<9}"
        print(row)

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

def export_to_excel(quiz_params: QuizParameters, output_data: List[Dict[str, Any]], question_numbers: List[int], output_folder: str = ""):
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

def export_to_csv(quiz_params: QuizParameters, output_data: List[Dict[str, Any]], question_numbers: List[int], output_folder: str = ""):
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

def main():
    """Main function for the console application."""
    try:
        print("="*80)
        print("QUIZ SCORE PROCESSOR")
        print("="*80)
        print("This application processes quiz grades from Excel or CSV files.")
        print("Please provide the following information:")

        # Get quiz parameters from user with error handling
        try:
            quiz_name = input("\nQuiz Name: ")
            if not quiz_name.strip():
                raise ValueError("Quiz name cannot be empty.")

            try:
                original_max_score = float(input("Original Maximum Quiz Score: "))
                if original_max_score <= 0:
                    raise ValueError("Original maximum score must be greater than zero.")
            except ValueError:
                raise ValueError("Invalid input for Original Maximum Quiz Score. Please enter a valid number.")

            try:
                new_max_score = float(input("New Desired Maximum Score: "))
                if new_max_score <= 0:
                    raise ValueError("New maximum score must be greater than zero.")
            except ValueError:
                raise ValueError("Invalid input for New Desired Maximum Score. Please enter a valid number.")

            try:
                original_question_value = float(input("Value of Each Question on Original Scale: "))
                if original_question_value <= 0:
                    raise ValueError("Question value must be greater than zero.")
            except ValueError:
                raise ValueError("Invalid input for Value of Each Question. Please enter a valid number.")
        except ValueError as e:
            print(f"\nError: {str(e)}")
            if input("Do you want to try again? (y/n): ").lower() == 'y':
                return main()  # Restart the application
            else:
                print("\nExiting application.")
                return

        # Create quiz parameters
        quiz_params = QuizParameters(
            quiz_name=quiz_name,
            original_max_score=original_max_score,
            new_max_score=new_max_score,
            original_question_value=original_question_value
        )

        # Verify calculation
        if not quiz_params.verify_calculation():
            print("\nWarning: Calculation verification failed. Please check your parameters.")
            print(f"Total Questions: {quiz_params.total_questions}")
            print(f"New Question Value: {quiz_params.new_question_value}")
            print(f"Expected New Max Score: {quiz_params.total_questions * quiz_params.new_question_value}")
            print(f"Actual New Max Score: {quiz_params.new_max_score}")

            choice = input("Do you want to (c)ontinue anyway, (r)estart with new parameters, or (q)uit? (c/r/q): ").lower()
            if choice == 'r':
                return main()  # Restart the application
            elif choice == 'q':
                print("\nExiting application.")
                return
            # Otherwise continue

        # Get file path from user
        while True:
            file_path = input("\nPath to Quiz Data File (Excel or CSV): ")
            if not file_path.strip():
                print("Error: File path cannot be empty.")
                if input("Do you want to try again? (y/n): ").lower() != 'y':
                    print("\nExiting application.")
                    return
                continue

            if not Path(file_path).exists():
                print(f"Error: File not found: {file_path}")
                if input("Do you want to try again? (y/n): ").lower() != 'y':
                    print("\nExiting application.")
                    return
                continue

            break  # Valid file path provided

        try:
            # Process the file
            print("\nProcessing file...")
            student_responses, question_numbers = process_file(file_path)

            # Convert scores
            print("Converting scores...")
            processed_responses = convert_scores(student_responses, quiz_params)

            # Verify conversion
            if not verify_conversion(processed_responses):
                print("\nWarning: Conversion verification failed. Please check your data.")
                choice = input("Do you want to (c)ontinue anyway, (r)estart with new parameters, or (q)uit? (c/r/q): ").lower()
                if choice == 'r':
                    return main()  # Restart the application
                elif choice == 'q':
                    print("\nExiting application.")
                    return
                # Otherwise continue

            # Generate output data
            print("Generating results...")
            output_data = generate_output_data(processed_responses, question_numbers)

            # Display results
            display_results(quiz_params, output_data, question_numbers)

            # Ask if user wants to export the results
            if input("\nDo you want to export the results to a file? (y/n): ").lower() == 'y':
                # Get the output folder
                output_folder = get_output_folder()

                # Ask for the export format
                while True:
                    export_format = input("Choose export format (1 for CSV, 2 for Excel): ")
                    if export_format == "1":
                        export_to_csv(quiz_params, output_data, question_numbers, output_folder)
                        break
                    elif export_format == "2":
                        export_to_excel(quiz_params, output_data, question_numbers, output_folder)
                        break
                    else:
                        print("Invalid choice. Please enter 1 for CSV or 2 for Excel.")

            # Ask if user wants to process another file
            if input("\nDo you want to process another file? (y/n): ").lower() == 'y':
                return main()  # Restart the application
            else:
                print("\nThank you for using Quiz Score Processor. Goodbye!")

        except Exception as e:
            print(f"\nError: {str(e)}")
            if input("\nDo you want to try again? (y/n): ").lower() == 'y':
                return main()  # Restart the application
            else:
                print("\nExiting application.")

    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Exiting application.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        print("Exiting application.")

if __name__ == "__main__":
    main()
