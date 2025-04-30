# Pyython instructions #
always use the virtual environment for running the code
if no virtual environment is found, create one using the command python -m venv .venv

# Code-generation instructions #

follow python PEP guidelines

use type declaration for functions, return vales, and parameters


# Test Generation instructions #
use as test framework pytest
for each non user interface feature or function write the tests to verify the functionality of the code
name tests using the format test_should{expected result}_given{input data or action} where the words in {} depend on each test
check for coverge after running tests for line coverage greater than 90%


# Commit message generation instructions

before commiting always check for code duplication and delete duplicated code

before committing check if the changed code runs 

use context specific information for generating commit messages

# Pull request title and description generation instructions

write a title with a short summary of the mayor changes to the solution

wirte a body describing: What changes were made and significant design decisions made