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

    # Conversion factor for scores
    conversion_factor = quiz_params.new_max_score / quiz_params.original_max_score

    for student_response in student_responses:
        # Create a processed response with converted total score
        processed_response = ProcessedResponse(
            **student_response.model_dump(),
            new_score=student_response.original_score * conversion_factor,
            question_new_scores={}
        )

        # Convert individual question scores
        for question_num, original_score in student_response.question_scores.items():
            processed_response.question_new_scores[question_num] = original_score * conversion_factor

        processed_responses.append(processed_response)

    return processed_responses


def verify_conversion(processed_responses: List[ProcessedResponse]) -> bool:
    """
    Verify that the sum of converted question scores equals the total converted score.

    Args:
        processed_responses: List of processed responses

    Returns:
        True if verification passes for all students, False otherwise
    """
    for response in processed_responses:
        # Sum of converted question scores
        sum_question_scores = sum(response.question_new_scores.values())

        # Check if the sum equals the total converted score (with small tolerance for floating point errors)
        if abs(sum_question_scores - response.new_score) > 0.0001:
            return False

    return True


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
