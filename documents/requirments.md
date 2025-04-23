write a web application for processing quiz grades read form an csv file.
the file contains several columns, I want to work with the following columns:
Team the student´s team
Student Name (First and Last)
Student First Name
Student Last Name
Email Address
Student ID
Score - the student score on the test
there is a row for each student.

there are two other columns for each question in the quiz.
to identify the question number you must check the prefix of the column name. for example the columns: 
1_Response
1_Score
identified the answeres and the scores for the first question.

Sure, here is a **clear and structured prompt** you could use to give these instructions to an assistant or system, whether human or automated:


I want to convert quiz scores to a new scoring scale. To do this, follow these step-by-step instructions:

#### 1. Ask the user for the following information:
- **Original maximum quiz score** (e.g., 15).
- **New desired maximum score** (e.g., 10).
- **Value of each question on the original scale** (e.g., 1 if all questions are equally weighted).

#### 2. Calculate:
- **Total number of questions** in the quiz by dividing the original maximum score by the value of each question:

  \[
  \text{TotalQuestions} = \frac{\text{OriginalMaxScore}}{\text{OriginalQuestionValue}}
  \]

- **New value per question**, dividing the new maximum score by the total number of questions:

  \[
  \text{NewQuestionValue} = \frac{\text{NewMaxScore}}{\text{TotalQuestions}}
  \]

- **Verify that**:

  \[
  \text{TotalQuestions} \times \text{NewQuestionValue} = \text{NewMaxScore}
  \]

#### 3. For each student:
- Enter the **original score obtained**.
- Calculate the **converted score** on the new scale by multiplying the number of correct answers by the new value per question:

  \[
  \text{NewScore} = \text{OriginalScore} \times \frac{\text{NewMaxScore}}{\text{OriginalMaxScore}}
  \]

#### 4. Display:
- the student answer for each question
- The **new value per question**.
- The **converted score for each student**.
- Confirm that the **sum of the new values for all questions equals the new total quiz score**.

