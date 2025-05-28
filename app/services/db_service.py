"""
Database service for storing quiz data in SQLite.
"""
import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from dotenv import load_dotenv

from app.models.quiz_data import QuizParameters, StudentResponse, ProcessedResponse

# Cargar variables de entorno del archivo .env
load_dotenv()

class DatabaseService:
    """Service for database operations"""
    # Obtener el nombre de la base de datos desde variables de entorno
    # o usar un valor predeterminado si no existe
    DB_NAME = os.getenv("DATABASE_NAME", "quiz_data.db")

    @classmethod
    def get_db_path(cls) -> str:
        """Get the path to the SQLite database file"""
        # Create database in the database directory
        root_dir = Path(__file__).resolve().parent.parent.parent
        db_dir = os.path.join(root_dir, "database")

        # Ensure the database directory exists
        os.makedirs(db_dir, exist_ok=True)

        # Asegurar que solo se use la base de datos en la carpeta database
        db_file_path = os.path.join(db_dir, cls.DB_NAME)
        print(f"Usando base de datos en: {db_file_path}")

        return db_file_path

    @classmethod
    def initialize_database(cls) -> None:
        """Initialize the database with required tables"""
        conn = sqlite3.connect(cls.get_db_path())
        cursor = conn.cursor()

        # Create quiz parameters table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_parameters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_name TEXT NOT NULL,
            original_max_score REAL NOT NULL,
            new_max_score REAL NOT NULL,
            original_question_value REAL NOT NULL,
            use_weighted_questions INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create question weights table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_parameter_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            weight REAL NOT NULL,
            FOREIGN KEY (quiz_parameter_id) REFERENCES quiz_parameters (id)
        )
        ''')

        # Create student responses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_parameter_id INTEGER NOT NULL,
            team TEXT,
            student_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            student_id TEXT NOT NULL,
            original_score REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_parameter_id) REFERENCES quiz_parameters (id)
        )
        ''')

        # Create question responses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_response_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            response TEXT,
            original_score REAL NOT NULL,
            FOREIGN KEY (student_response_id) REFERENCES student_responses (id)
        )
        ''')

        # Create processed responses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_response_id INTEGER NOT NULL,
            new_score REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_response_id) REFERENCES student_responses (id)
        )
        ''')

        # Create processed question scores table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_question_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            processed_response_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            new_score REAL NOT NULL,
            FOREIGN KEY (processed_response_id) REFERENCES processed_responses (id)
        )
        ''')

        conn.commit()
        conn.close()

    @classmethod
    def save_quiz_data(cls, quiz_params: QuizParameters,
                      student_responses: List[StudentResponse],
                      processed_responses: List[ProcessedResponse],
                      sheet_name: str) -> None:
        """Save all quiz data to the database"""
        conn = sqlite3.connect(cls.get_db_path())
        cursor = conn.cursor()

        try:
            # 1. Insert quiz parameters
            cursor.execute('''
            INSERT INTO quiz_parameters 
            (quiz_name, original_max_score, new_max_score, original_question_value, use_weighted_questions) 
            VALUES (?, ?, ?, ?, ?)
            ''', (
                quiz_params.quiz_name,  # Usar el nombre del quiz que ingresó el usuario
                quiz_params.original_max_score,
                quiz_params.new_max_score,
                quiz_params.original_question_value,
                1 if quiz_params.use_weighted_questions else 0
            ))

            quiz_parameter_id = cursor.lastrowid

            # 2. Insert question weights if using weighted questions
            if quiz_params.use_weighted_questions:
                for question_num, weight in quiz_params.question_weights.items():
                    cursor.execute('''
                    INSERT INTO question_weights (quiz_parameter_id, question_number, weight)
                    VALUES (?, ?, ?)
                    ''', (quiz_parameter_id, question_num, weight))

            # 3. Insert student responses and processed responses
            for i, student_response in enumerate(student_responses):
                cursor.execute('''
                INSERT INTO student_responses 
                (quiz_parameter_id, team, student_name, first_name, last_name, 
                 email, student_id, original_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    quiz_parameter_id,
                    student_response.team,
                    student_response.student_name,
                    student_response.first_name,
                    student_response.last_name,
                    student_response.email,
                    student_response.student_id,
                    student_response.original_score
                ))

                student_response_id = cursor.lastrowid

                # Insert question responses
                for question_num, response in student_response.responses.items():
                    score = student_response.question_scores.get(question_num, 0)
                    cursor.execute('''
                    INSERT INTO question_responses 
                    (student_response_id, question_number, response, original_score)
                    VALUES (?, ?, ?, ?)
                    ''', (student_response_id, question_num, response, score))

                # Insert processed response if available
                if i < len(processed_responses):
                    processed = processed_responses[i]
                    cursor.execute('''
                    INSERT INTO processed_responses 
                    (student_response_id, new_score)
                    VALUES (?, ?)
                    ''', (student_response_id, processed.new_score))

                    processed_response_id = cursor.lastrowid

                    # Insert processed question scores
                    for question_num, new_score in processed.question_new_scores.items():
                        cursor.execute('''
                        INSERT INTO processed_question_scores 
                        (processed_response_id, question_number, new_score)
                        VALUES (?, ?, ?)
                        ''', (processed_response_id, question_num, new_score))

            conn.commit()
            print(f"Datos guardados exitosamente en la base de datos: {cls.get_db_path()}")

        except sqlite3.Error as e:
            conn.rollback()
            print(f"Error al guardar en la base de datos: {e}")

        finally:
            conn.close()

    @classmethod
    def get_all_quizzes(cls) -> List[Dict]:
        """Get all quizzes from the database"""
        conn = sqlite3.connect(cls.get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
        SELECT * FROM quiz_parameters
        ORDER BY created_at DESC
        ''')

        quizzes = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return quizzes
