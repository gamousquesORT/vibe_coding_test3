"""
Quiz service for handling quiz score conversion.
"""
from typing import List, Dict, Tuple
from app.models.quiz_data import QuizParameters, StudentResponse, ProcessedResponse


def convert_scores(
    student_responses: List[StudentResponse], 
    quiz_params: QuizParameters
) -> List[ProcessedResponse]:
    """
    Convert student scores based on the provided quiz parameters.

    Args:
        student_responses: List of student responses
        quiz_params: Quiz parameters for conversion

    Returns:
        List of processed responses with converted scores
    """
    processed_responses = []

    # Conversion factor for total score (used for non-weighted questions)
    conversion_factor = quiz_params.new_max_score / quiz_params.original_max_score

    for student_response in student_responses:
        # Initialize processed response with placeholder for new_score
        processed_response = ProcessedResponse(
            **student_response.model_dump(),
            new_score=0.0,  # Will be updated after calculating individual scores
            question_new_scores={}
        )

        # Convert individual question scores using the appropriate method
        for question_num, original_score in student_response.question_scores.items():
            # Use the method to calculate question scores based on weights
            new_score = quiz_params.calculate_new_question_score(question_num, original_score)
            processed_response.question_new_scores[question_num] = new_score

        # If using weighted questions, set the total score as the sum of individual scores
        # Otherwise, use the simple conversion factor
        if quiz_params.use_weighted_questions:
            processed_response.new_score = sum(processed_response.question_new_scores.values())
        else:
            processed_response.new_score = student_response.original_score * conversion_factor

        processed_responses.append(processed_response)

    return processed_responses


def verify_conversion(processed_responses: List[ProcessedResponse], quiz_params: QuizParameters) -> bool:
    """
    Verify that the sum of converted question scores equals the total converted score.

    Args:
        processed_responses: List of processed responses
        quiz_params: Quiz parameters used for conversion

    Returns:
        True if verification passes for all students, False otherwise
    """
    all_valid = True

    print("\nVERIFICATION DETAILS:")
    print("-" * 80)
    print(f"{'Student Name':<20} {'Sum of Question Scores':<25} {'Total Score':<15} {'Difference':<15} {'Status':<10}")
    print("-" * 80)

    for response in processed_responses:
        # Sum of converted question scores
        sum_question_scores = sum(response.question_new_scores.values())

        # Calculate the difference
        difference = abs(sum_question_scores - response.new_score)

        # Check if the sum equals the total converted score (with small tolerance for floating point errors)
        is_valid = difference <= 0.0001

        # Print verification details for this student
        status = "✓ PASS" if is_valid else "✗ FAIL"
        print(f"{response.student_name:<20} {sum_question_scores:<25.4f} {response.new_score:<15.4f} {difference:<15.4f} {status:<10}")

        # Print detailed calculation information for all students
        print(f"  Calculation details for {response.student_name}:")

        # Print general conversion information
        print(f"    Original Max Score: {quiz_params.original_max_score}")
        print(f"    New Max Score: {quiz_params.new_max_score}")
        print(f"    Original Question Value: {quiz_params.original_question_value}")

        if quiz_params.use_weighted_questions:
            print(f"    Using weighted questions: Yes")
            print(f"    Total Weight: {sum(quiz_params.question_weights.values())}")
        else:
            print(f"    Using weighted questions: No")
            print(f"    Simple Conversion Factor: {quiz_params.new_max_score / quiz_params.original_max_score:.4f}")

        # Print details for each question
        for q_num, new_score in response.question_new_scores.items():
            original_score = response.question_scores.get(q_num, 0)
            print(f"\n    Question {q_num}:")
            print(f"      Original Score: {original_score:.4f}")
            print(f"      New Score: {new_score:.4f}")

            if quiz_params.use_weighted_questions:
                weight = quiz_params.get_question_weight(q_num)
                total_weight = sum(quiz_params.question_weights.values())
                original_question_max = quiz_params.original_question_value
                new_question_max = quiz_params.new_max_score * weight / total_weight
                conversion_factor = new_question_max / original_question_max

                print(f"      Weight: {weight:.4f}")
                print(f"      % of Total: {(weight / total_weight) * 100:.2f}%")
                print(f"      New Question Max: {new_question_max:.4f}")
                print(f"      Conversion Factor: {conversion_factor:.4f}")
                print(f"      Calculation: {original_score:.4f} × {conversion_factor:.4f} = {original_score * conversion_factor:.4f}")
            else:
                conversion_factor = quiz_params.new_max_score / quiz_params.original_max_score
                print(f"      Conversion Factor: {conversion_factor:.4f}")
                print(f"      Calculation: {original_score:.4f} × {conversion_factor:.4f} = {original_score * conversion_factor:.4f}")

    print("-" * 80)
    print(f"Overall verification status: {'✓ PASSED' if all_valid else '✗ FAILED'}")

    return all_valid


def generate_output_data(
    processed_responses: List[ProcessedResponse], 
    question_numbers: List[int]
) -> List[Dict]:
    """
    Generate output data for display or export.

    Args:
        processed_responses: List of processed responses
        question_numbers: List of question numbers

    Returns:
        List of dictionaries with formatted output data
    """
    # Debug: Print processed responses
    print("Processed responses:")
    for i, response in enumerate(processed_responses):
        print(f"Response {i+1}:")
        print(f"  Team: {response.team}")
        print(f"  Student Name: {response.student_name}")
        print(f"  First Name: {response.first_name}")
        print(f"  Last Name: {response.last_name}")
        print(f"  Student ID: {response.student_id}")
        print(f"  Original Score: {response.original_score}")
        print(f"  New Score: {response.new_score}")
        print(f"  Responses: {response.responses}")
        print(f"  Question Scores: {response.question_scores}")
        print(f"  Question New Scores: {response.question_new_scores}")

    # Debug: Print question numbers
    print("Question numbers:", question_numbers)

    output_data = []

    for response in processed_responses:
        student_data = {
            "Team": response.team or "",
            "Student Name": response.student_name,
            "First Name": response.first_name,
            "Last Name": response.last_name,
            "Student ID": response.student_id,
            "Original Score": response.original_score,
            "Converted Score": round(response.new_score, 2)
        }

        # Debug: Print student data
        print(f"Student data for {response.student_name}:")
        print(student_data)

        # Add question-specific data
        for q_num in question_numbers:
            if q_num in response.responses:
                student_data[f"Q{q_num} Response"] = response.responses[q_num]

            if q_num in response.question_scores:
                student_data[f"Q{q_num} Original Score"] = response.question_scores[q_num]

            if q_num in response.question_new_scores:
                student_data[f"Q{q_num} Converted Score"] = round(response.question_new_scores[q_num], 2)

        output_data.append(student_data)

    return output_data
