from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Any
import os
import tempfile
from app.services.file_service import FileService
from app.services.quiz_service import QuizService
from app.models.quiz_data import QuizParameters, QuizData

router = APIRouter()

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# In-memory storage for quiz data (in a real app, this would be a database or session)
_quiz_data: Optional[QuizData] = None


def get_quiz_data_from_session() -> QuizData:
    """Get quiz data from session."""
    if _quiz_data is None:
        raise HTTPException(status_code=404, detail="No quiz data found. Please upload a file first.")
    return _quiz_data


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request):
    """Render the upload form."""
    return templates.TemplateResponse("upload.html", {"request": request})


@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    original_max_score: float = Form(...),
    new_max_score: float = Form(...),
    original_question_value: float = Form(...)
):
    """Process the uploaded file and quiz parameters."""
    global _quiz_data
    
    # Create quiz parameters
    params = QuizParameters(
        original_max_score=original_max_score,
        new_max_score=new_max_score,
        original_question_value=original_question_value
    )
    
    # Verify calculation
    if not QuizService.verify_calculation(params):
        return templates.TemplateResponse(
            "upload.html", 
            {
                "request": request, 
                "error": "Invalid parameters. Please check that the original maximum score is divisible by the original question value."
            }
        )
    
    # Save uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        temp_file_path = temp_file.name
        content = await file.read()
        temp_file.write(content)
    
    try:
        # Read the file
        df = FileService.read_file(temp_file_path)
        
        # Process the data
        _quiz_data = QuizService.process_dataframe(df, params)
        
        # Redirect to results page
        return RedirectResponse(url="/results", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "upload.html", 
            {
                "request": request, 
                "error": f"Error processing file: {str(e)}"
            }
        )
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.get("/results", response_class=HTMLResponse)
async def results(request: Request, quiz_data: QuizData = Depends(get_quiz_data_from_session)):
    """Display the results of the quiz score conversion."""
    # Get question numbers
    question_numbers = sorted(list(quiz_data.students[0].responses.keys())) if quiz_data.students else []
    
    return templates.TemplateResponse(
        "results.html", 
        {
            "request": request, 
            "quiz_data": quiz_data,
            "question_numbers": question_numbers
        }
    )