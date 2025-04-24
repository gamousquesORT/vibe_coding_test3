import pandas as pd
from typing import Union, List, Dict, Any
import os


class FileService:
    """Service for handling file operations related to quiz data."""
    
    @staticmethod
    def read_file(file_path: str) -> pd.DataFrame:
        """
        Read a file (Excel or CSV) and return its contents as a pandas DataFrame.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            DataFrame containing the file contents
            
        Raises:
            ValueError: If the file format is not supported
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.xlsx' or file_extension == '.xls':
            return pd.read_excel(file_path)
        elif file_extension == '.csv':
            return pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    @staticmethod
    def save_file(df: pd.DataFrame, file_path: str) -> None:
        """
        Save a DataFrame to a file (Excel or CSV).
        
        Args:
            df: DataFrame to save
            file_path: Path where to save the file
            
        Raises:
            ValueError: If the file format is not supported
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.xlsx' or file_extension == '.xls':
            df.to_excel(file_path, index=False)
        elif file_extension == '.csv':
            df.to_csv(file_path, index=False)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")