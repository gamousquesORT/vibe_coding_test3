write a web application for processing quiz grades read form an csv or excel file.
the file contains several columns, I want to work only with the following columns:
Team
Student Name
First Name
Last Name
Email Address
Student ID
Score - the student score on the test
there is a row for each student.

the file contains servarl column wiche theri names are prefixed with a number, for example: 1_Response meaning that that column has on its cells the response for question 1 
the app will work with the following columns for each question
1_Response
1_Score



I want to convert the quiz scores to a new scoring scale. To do this, follow these step-by-step instructions:

#### 1. Ask the user for the following information:
- **Original maximum quiz score** (e.g., 15).
- **New desired maximum score** (e.g., 10).
- **Value of each question on the original scale all questions are equally weighted).**

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

#### 4. Display in grid format:
- the student answer for each question
- The **new value per question**.
- The **converted score for each student**.
- Confirm that the **sum of the new values for all questions equals the new total quiz score**.

