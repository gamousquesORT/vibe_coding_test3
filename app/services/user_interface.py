"""
User interface for the quiz score processor application.
"""
from typing import List, Dict, Any, Tuple
from pathlib import Path

from app.models.quiz_data import QuizParameters, StudentResponse, ProcessedResponse


class UserInterface:
    """Class for handling user interface interactions."""
    
    @staticmethod
    def display_welcome():
        """Display welcome message and application information."""
        print("="*80)
        print("QUIZ SCORE PROCESSOR")
        print("="*80)
        print("This application processes quiz grades from Excel or CSV files.")
        print("Please provide the following information:")
    
    @staticmethod
    def get_quiz_parameters() -> QuizParameters:
        """
        Get quiz parameters from user input.
        
        Returns:
            QuizParameters object with user-provided values
        """
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

            # Ask if user wants to use weighted questions
            use_weighted_questions = input("\nDo you want to assign different weights to questions? (y/n): ").lower() == 'y'

            # Create quiz parameters with default values
            quiz_params = QuizParameters(
                quiz_name=quiz_name,
                original_max_score=original_max_score,
                new_max_score=new_max_score,
                original_question_value=original_question_value,
                use_weighted_questions=use_weighted_questions
            )

            # If using weighted questions, get the weights
            if use_weighted_questions:
                print("\nYou'll now be asked to enter weights for each question.")
                print("Weights determine the relative importance of each question.")
                print("For example, if question 1 has weight 2 and question 2 has weight 1,")
                print("question 1 will be worth twice as much as question 2 in the final score.")

                # Get the number of questions
                try:
                    num_questions = int(input("\nHow many questions are in the quiz? "))
                    if num_questions <= 0:
                        raise ValueError("Number of questions must be greater than zero.")
                except ValueError:
                    print("Invalid input. Using calculated number of questions.")
                    num_questions = int(quiz_params.total_questions)
                    print(f"Calculated number of questions: {num_questions}")

                # Get weights for each question
                question_weights = {}
                for i in range(1, num_questions + 1):
                    try:
                        weight = float(input(f"Weight for question {i}: "))
                        if weight <= 0:
                            print("Weight must be greater than zero. Using default weight of 1.")
                            weight = 1.0
                        question_weights[i] = weight
                    except ValueError:
                        print("Invalid input. Using default weight of 1.")
                        question_weights[i] = 1.0

                # Update quiz parameters with question weights
                quiz_params.question_weights = question_weights

                print("\nQuestion weights:")
                for q_num, weight in question_weights.items():
                    print(f"Question {q_num}: {weight}")

                # Calculate and display the total weight
                total_weight = sum(question_weights.values())
                print(f"Total weight: {total_weight}")

                # Calculate and display the percentage of total for each question
                print("\nPercentage of total for each question:")
                for q_num, weight in question_weights.items():
                    percentage = (weight / total_weight) * 100
                    print(f"Question {q_num}: {percentage:.2f}%")

                # Calculate and display the new maximum score for each question
                print("\nNew maximum score for each question:")
                for q_num, weight in question_weights.items():
                    new_max = (weight / total_weight) * quiz_params.new_max_score
                    print(f"Question {q_num}: {new_max:.2f}")

            return quiz_params
            
        except ValueError as e:
            raise ValueError(str(e))
    
    @staticmethod
    def verify_calculation(quiz_params: QuizParameters) -> bool:
        """
        Verify calculation and ask user what to do if verification fails.
        
        Args:
            quiz_params: Quiz parameters to verify
            
        Returns:
            True to continue, False to restart or quit
        """
        if not quiz_params.verify_calculation():
            print("\nWarning: Calculation verification failed. Please check your parameters.")
            print(f"Total Questions: {quiz_params.total_questions}")
            print(f"New Question Value: {quiz_params.new_question_value}")
            print(f"Expected New Max Score: {quiz_params.total_questions * quiz_params.new_question_value}")
            print(f"Actual New Max Score: {quiz_params.new_max_score}")

            choice = input("Do you want to (c)ontinue anyway, (r)estart with new parameters, or (q)uit? (c/r/q): ").lower()
            if choice == 'r':
                return False
            elif choice == 'q':
                print("\nExiting application.")
                return False
            # Otherwise continue
            return True
        return True
    
    @staticmethod
    def get_file_path() -> str:
        """
        Get file path from user input.
        
        Returns:
            Path to the file or empty string to quit
        """
        while True:
            file_path = input("\nPath to Quiz Data File (Excel or CSV): ")
            if not file_path.strip():
                print("Error: File path cannot be empty.")
                if input("Do you want to try again? (y/n): ").lower() != 'y':
                    print("\nExiting application.")
                    return ""
                continue

            if not Path(file_path).exists():
                print(f"Error: File not found: {file_path}")
                if input("Do you want to try again? (y/n): ").lower() != 'y':
                    print("\nExiting application.")
                    return ""
                continue

            return file_path  # Valid file path provided
    
    @staticmethod
    def verify_conversion(processed_responses: List[ProcessedResponse], quiz_params: QuizParameters) -> bool:
        """
        Verify conversion and ask user what to do if verification fails.
        
        Args:
            processed_responses: List of processed responses
            quiz_params: Quiz parameters
            
        Returns:
            True to continue, False to restart or quit
        """
        from app.services.quiz_service import verify_conversion
        
        if not verify_conversion(processed_responses, quiz_params):
            print("\nWarning: Conversion verification failed. Please check your data.")
            choice = input("Do you want to (c)ontinue anyway, (r)estart with new parameters, or (q)uit? (c/r/q): ").lower()
            if choice == 'r':
                return False
            elif choice == 'q':
                print("\nExiting application.")
                return False
            # Otherwise continue
            return True
        return True
    
    @staticmethod
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

        # Display weighted question information if applicable
        if quiz_params.use_weighted_questions:
            print("\nWEIGHTED QUESTIONS:")
            print("-"*80)
            print(f"{'Question':<10} {'Weight':<10} {'% of Total':<15} {'New Max Score':<15}")
            print("-"*80)

            total_weight = sum(quiz_params.question_weights.values())
            for q_num in sorted(quiz_params.question_weights.keys()):
                weight = quiz_params.question_weights[q_num]
                percentage = (weight / total_weight) * 100
                new_max = (weight / total_weight) * quiz_params.new_max_score
                print(f"{q_num:<10} {weight:<10.2f} {percentage:<15.2f}% {new_max:<15.2f}")

            print(f"{'Total':<10} {total_weight:<10.2f} {'100.00':<15}% {quiz_params.new_max_score:<15.2f}")

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
    
    @staticmethod
    def ask_export() -> bool:
        """
        Ask if user wants to export results.
        
        Returns:
            True if user wants to export, False otherwise
        """
        return input("\nDo you want to export the results to a file? (y/n): ").lower() == 'y'
    
    @staticmethod
    def get_export_format() -> str:
        """
        Get export format from user.
        
        Returns:
            "csv" or "excel" based on user choice
        """
        while True:
            export_format = input("Choose export format (1 for CSV, 2 for Excel): ")
            if export_format == "1":
                return "csv"
            elif export_format == "2":
                return "excel"
            else:
                print("Invalid choice. Please enter 1 for CSV or 2 for Excel.")
    
    @staticmethod
    def ask_process_another() -> bool:
        """
        Ask if user wants to process another file.
        
        Returns:
            True if user wants to process another file, False otherwise
        """
        return input("\nDo you want to process another file? (y/n): ").lower() == 'y'
    
    @staticmethod
    def ask_try_again() -> bool:
        """
        Ask if user wants to try again after an error.
        
        Returns:
            True if user wants to try again, False otherwise
        """
        return input("\nDo you want to try again? (y/n): ").lower() == 'y'
    
    @staticmethod
    def display_goodbye():
        """Display goodbye message."""
        print("\nThank you for using Quiz Score Processor. Goodbye!")
    
    @staticmethod
    def display_error(error_message: str):
        """
        Display error message.
        
        Args:
            error_message: Error message to display
        """
        print(f"\nError: {error_message}")