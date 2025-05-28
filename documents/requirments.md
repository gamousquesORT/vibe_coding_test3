write a web application in python for processing quiz grades read form an csv or excel file.

Excel file content
the file contains several columns, I want to work only with the following columns:
Team
Student Name
First Name
Last Name
Email Address
Student ID
Score 
there is a row with the values and scores for each student.

the file contains several columns with names prefixed with a number, for example: 1_Response 
this means that the column has on its cells the response for question 1

the app will work with the following columns for each question
1_Response
1_Score

I want to convert the quiz scores to a new scoring scale. To do this, follow these step-by-step instructions:

#### 1. Ask the user for the following information:
- ** the quiz name** (e.g., "Quiz 1"). and it should be used as the name of the output file.
- **Original maximum quiz score** (e.g., 15).
- **New desired maximum score** (e.g., 10).
- **Value of each question on the original scale. all questions are equally weighted.

#### 2. Calculate:
- **Total number of questions** in the quiz by dividing the original maximum score by the value of each question:


 TotalQuestions = OriginalMaxScore\OriginalQuestionValue


- **New value per question**, dividing the new maximum score by the total number of questions:

  NewQuestionValue = NewMaxScore\TotalQuestions
- 

- **Verify that**:

  TotalQuestions * NewQuestionValue = NewMaxScore


#### 3. For each student:
- Calculate the **converted score** to the new scale by multiplying the score of each question by  (NewMaxScore\OriginalMaxScore)
  NewScore = OriginalScore * (NewMaxScore\OriginalMaxScore)

#### 4. Display in grid format:
- Team
- Student Name
- First Name
- Last Name
- -Student ID
- the **converted total score** for each student.
- for each question:
- the student answere for each question
- The **orignal score for question**.
- The **converted score for each question**.

- Confirm that the **sum of the new values for all questions equals the new total quiz score**.

