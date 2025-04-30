# Quiz Score Processor

A console application for processing quiz grades from Excel or CSV files and converting them to a new scoring scale.

## Features

- Process Excel or CSV files containing quiz data
- Convert scores from original scale to a new scale
- Display detailed breakdown of scores for each student
- Verify score conversion accuracy
- Export results to CSV

## Requirements

- Python 3.8+
- Pandas
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/quiz-score-processor.git
   cd quiz-score-processor
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```
   python main.py
   ```

2. Follow the prompts to enter:
   - Quiz Name
   - Original Maximum Quiz Score
   - New Desired Maximum Score
   - Value of Each Question on Original Scale
   - Path to Quiz Data File (Excel or CSV)

3. The application will process the file and display the results

4. You can choose to export the results to a CSV file

## File Format

For Excel files (.xlsx, .xls), the application specifically reads data from the "Team Analysis" sheet.
For CSV files, the application reads the entire file.

The data should contain the following columns:
- Team
- Student Name
- First Name
- Last Name
- Email Address
- Student ID
- Score
- Question responses and scores (e.g., 1_Response, 1_Score, 2_Response, 2_Score, etc.)

## Testing

Run tests using pytest:
```
pytest
```

Check test coverage:
```
pytest --cov=app tests/
```

## Project Structure

- `app/`: Main application package
  - `models/`: Data models
  - `services/`: Business logic
- `tests/`: Test files
- `main.py`: Application entry point
- `requirements.txt`: Dependencies

## License

MIT
