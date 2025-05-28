"""
Router for quiz-related endpoints.
"""
from fastapi import APIRouter, Request, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import pandas as pd
import os
from pathlib import Path

from app.models.quiz_data import QuizParameters
from app.services.file_service import process_file
from app.services.quiz_service import convert_scores, verify_conversion, generate_output_data

# Create router with prefix
router = APIRouter(prefix="/quiz")

# Set up templates
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the index page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request):
    """Render the upload form."""
    return templates.TemplateResponse("upload.html", {"request": request})


@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    quiz_name: str = Form(...),
    original_max_score: float = Form(...),
    new_max_score: float = Form(...),
    original_question_value: float = Form(...)
):
    """
    Handle file upload and quiz parameter submission.

    Args:
        request: The request object
        file: The uploaded file
        quiz_name: Name of the quiz
        original_max_score: Original maximum quiz score
        new_max_score: New desired maximum score
        original_question_value: Value of each question on the original scale

    Returns:
        Redirect to results page
    """
    try:
        # Create quiz parameters
        quiz_params = QuizParameters(
            quiz_name=quiz_name,
            original_max_score=original_max_score,
            new_max_score=new_max_score,
            original_question_value=original_question_value
        )

        # Verify calculation
        if not quiz_params.verify_calculation():
            raise HTTPException(
                status_code=400, 
                detail="Calculation verification failed. Please check your parameters."
            )

        # Process the file
        student_responses, question_numbers = await process_file(file)

        # Convert scores
        processed_responses = convert_scores(student_responses, quiz_params)

        # Verify conversion
        if not verify_conversion(processed_responses):
            raise HTTPException(
                status_code=400, 
                detail="Conversion verification failed. Please check your data."
            )

        # Generate output data
        output_data = generate_output_data(processed_responses, question_numbers)

        # Debug: Print output data
        print("Output data to be passed to template:")
        for i, student in enumerate(output_data):
            print(f"Student {i+1}:")
            for key, value in student.items():
                print(f"  {key}: {value}")

        # Debug: Print question numbers
        print("Question numbers to be passed to template:", question_numbers)

        # Store data in session or temporary storage
        # For simplicity, we'll pass it directly to the template
        return templates.TemplateResponse(
            "results.html", 
            {
                "request": request,
                "quiz_params": quiz_params,
                "output_data": output_data,
                "question_numbers": question_numbers
            }
        )

    except Exception as e:
        # Handle errors
        return templates.TemplateResponse(
            "upload.html", 
            {
                "request": request,
                "error": str(e)
            }
        )


@router.get("/results", response_class=HTMLResponse)
async def results(request: Request):
    """Render the results page."""
    # This endpoint would normally retrieve data from session or storage
    # For now, it just redirects to the upload form
    return RedirectResponse(url="/quiz/upload")
