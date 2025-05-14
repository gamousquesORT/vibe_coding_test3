"""
Database service for storing quiz data in SQLite.
"""
import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

from app.models.quiz_data import QuizParameters, ProcessedResponse


class DatabaseService:
    """Class for handling database operations for quiz data."""
    
    DB_FILE = "quiz_scores.db"
    
    @staticmethod
    def get_db_path() -> Path:
        """
        Get the path to the database file.
        
        Returns:
            Path to the database file
        """
        # Create a data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        return data_dir / DatabaseService.DB_FILE
    
    @staticmethod
    def initialize_database() -> None:
        """
        Initialize the database by creating necessary tables if they don't exist.
        """
        db_path = DatabaseService.get_db_path()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create quizzes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_name TEXT NOT NULL,
            original_max_score REAL NOT NULL,
            new_max_score REAL NOT NULL,
            original_question_value REAL NOT NULL,
            use_weighted_questions INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create question_weights table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            weight REAL NOT NULL,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id),
            UNIQUE (quiz_id, question_number)
        )
        ''')
        
        # Create students table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            team TEXT,
            student_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            student_id TEXT NOT NULL,
            original_score REAL NOT NULL,
            new_score REAL NOT NULL,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id),
            UNIQUE (quiz_id, student_id)
        )
        ''')
        
        # Create question_responses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            response TEXT,
            original_score REAL,
            new_score REAL,
            FOREIGN KEY (student_id) REFERENCES students (id),
            UNIQUE (student_id, question_number)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def store_quiz_data(
        quiz_params: QuizParameters, 
        processed_responses: List[ProcessedResponse],
        question_numbers: List[int]
    ) -> int:
        """
        Store quiz data in the database.
        
        Args:
            quiz_params: Quiz parameters
            processed_responses: List of processed responses
            question_numbers: List of question numbers
            
        Returns:
            ID of the inserted quiz
        """
        db_path = DatabaseService.get_db_path()
        
        # Ensure database is initialized
        DatabaseService.initialize_database()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Begin transaction
            conn.execute("BEGIN TRANSACTION")
            
            # Insert quiz parameters
            cursor.execute('''
            INSERT INTO quizzes (
                quiz_name, original_max_score, new_max_score, 
                original_question_value, use_weighted_questions
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                quiz_params.quiz_name,
                quiz_params.original_max_score,
                quiz_params.new_max_score,
                quiz_params.original_question_value,
                1 if quiz_params.use_weighted_questions else 0
            ))
            
            quiz_id = cursor.lastrowid
            
            # Insert question weights if using weighted questions
            if quiz_params.use_weighted_questions:
                for question_num, weight in quiz_params.question_weights.items():
                    cursor.execute('''
                    INSERT INTO question_weights (quiz_id, question_number, weight)
                    VALUES (?, ?, ?)
                    ''', (quiz_id, question_num, weight))
            
            # Insert student data and question responses
            for response in processed_responses:
                cursor.execute('''
                INSERT INTO students (
                    quiz_id, team, student_name, first_name, last_name,
                    email, student_id, original_score, new_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    quiz_id,
                    response.team,
                    response.student_name,
                    response.first_name,
                    response.last_name,
                    response.email,
                    response.student_id,
                    response.original_score,
                    response.new_score
                ))
                
                student_id = cursor.lastrowid
                
                # Insert question responses and scores
                for q_num in question_numbers:
                    response_text = response.responses.get(q_num, "")
                    original_score = response.question_scores.get(q_num, 0.0)
                    new_score = response.question_new_scores.get(q_num, 0.0)
                    
                    cursor.execute('''
                    INSERT INTO question_responses (
                        student_id, question_number, response, original_score, new_score
                    ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        student_id,
                        q_num,
                        response_text,
                        original_score,
                        new_score
                    ))
            
            # Commit transaction
            conn.commit()
            
            print(f"\nQuiz data stored in database: {db_path}")
            return quiz_id
            
        except Exception as e:
            # Rollback transaction on error
            conn.rollback()
            print(f"Error storing quiz data: {str(e)}")
            raise
        finally:
            conn.close()