import sys
from typing import List, Dict, Any

from app.models.quiz_data import QuizParameters, StudentResponse, ProcessedResponse
from app.services.quiz_service import convert_scores, generate_output_data
from app.services.file_handler import FileHandler
from app.services.user_interface import UserInterface


def main():
    """Main function for the console application."""
    try:
        # Display welcome message
        UserInterface.display_welcome()

        # Get quiz parameters from user
        try:
            quiz_params = UserInterface.get_quiz_parameters()
        except ValueError as e:
            UserInterface.display_error(str(e))
            if UserInterface.ask_try_again():
                return main()  # Restart the application
            else:
                print("\nExiting application.")
                return

        # Verify calculation
        if not UserInterface.verify_calculation(quiz_params):
            return main()  # Restart the application

        # Get file path from user
        file_path = UserInterface.get_file_path()
        if not file_path:  # Empty string means user wants to quit
            return

        try:
            # Process the file
            print("\nProcessing file...")
            student_responses, question_numbers = FileHandler.process_file(file_path)

            # Convert scores
            print("Converting scores...")
            processed_responses = convert_scores(student_responses, quiz_params)

            # Verify conversion
            if not UserInterface.verify_conversion(processed_responses, quiz_params):
                return main()  # Restart the application

            # Generate output data
            print("Generating results...")
            output_data = generate_output_data(processed_responses, question_numbers)

            # Display results
            UserInterface.display_results(quiz_params, output_data, question_numbers)

            # Automatically export the results after processing each file
            # Get the output folder
            output_folder = FileHandler.get_output_folder()

            # Export to Excel by default
            print("\nAutomatically exporting results to Excel...")
            FileHandler.export_to_excel(quiz_params, output_data, question_numbers, output_folder)

            # Ask if user wants to process another file
            if UserInterface.ask_process_another():
                return main()  # Restart the application
            else:
                UserInterface.display_goodbye()

        except Exception as e:
            UserInterface.display_error(str(e))
            if UserInterface.ask_try_again():
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
