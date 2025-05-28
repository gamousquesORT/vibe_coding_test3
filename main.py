import sys
from typing import List, Dict, Any

from app.models.quiz_data import QuizParameters, StudentResponse, ProcessedResponse
from app.services.quiz_service import convert_scores, generate_output_data
from app.services.file_handler import FileHandler
from app.services.user_interface import UserInterface
from app.services.db_service import DatabaseService


def main():
    """Main function for the console application."""
    # Initialize database (solo una vez al inicio del programa)
    DatabaseService.initialize_database()

    try:
        # Display welcome message
        UserInterface.display_welcome()

        process_another = True
        while process_another:
            try:
                # Get quiz parameters from user
                quiz_params = UserInterface.get_quiz_parameters()
            except ValueError as e:
                UserInterface.display_error(str(e))
                if UserInterface.ask_try_again():
                    continue  # Reintentar con este quiz
                else:
                    print("\nExiting application.")
                    return

            # Verify calculation
            if not UserInterface.verify_calculation(quiz_params):
                continue  # Reintentar con este quiz

            # Get file path from user
            file_path = UserInterface.get_file_path()
            if not file_path:  # Empty string means user wants to quit
                return

            try:
                # Process the file
                print("\nProcessing file...")
                student_responses, question_numbers, sheet_name = FileHandler.process_file(file_path)

                # Convert scores
                print("Converting scores...")
                processed_responses = convert_scores(student_responses, quiz_params)

                # Verify conversion
                if not UserInterface.verify_conversion(processed_responses, quiz_params):
                    continue  # Reintentar con este quiz

                # Generate output data
                print("Generating results...")
                output_data = generate_output_data(processed_responses, question_numbers)

                # Save data to SQLite database
                print("\nGuardando datos en la base de datos SQLite...")
                DatabaseService.save_quiz_data(quiz_params, student_responses, processed_responses, sheet_name)

                # Display results
                UserInterface.display_results(quiz_params, output_data, question_numbers)

                # Automatically export the results after processing each file
                # Get the output folder
                output_folder = FileHandler.get_output_folder()

                # Export to Excel by default
                print("\nAutomatically exporting results to Excel...")
                FileHandler.export_to_excel(quiz_params, output_data, question_numbers, output_folder, sheet_name)

                # Ask if user wants to process another file
                process_another = UserInterface.ask_process_another()
                if not process_another:
                    UserInterface.display_goodbye()

            except Exception as e:
                UserInterface.display_error(str(e))
                if UserInterface.ask_try_again():
                    continue  # Reintentar con otro archivo
                else:
                    print("\nExiting application.")
                    process_another = False

    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Exiting application.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        print("Exiting application.")

if __name__ == "__main__":
    main()
