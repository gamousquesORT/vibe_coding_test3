# Documentation Instructions #

append and save the history of our chat to the chat-history.md file on the folder copilot_documents, add a timestamp on each entry

# Pyython instructions #
always use the virtul environment for running the code
if no virtual environment is found, create one using the command python -m venv .venv

# Code-generation instructions #

follow python PEP guidelines

use type declaration for functions return and parameters


# Test Generation instructions #

use test driven development.
for each feature or function write a test before implementing the code
propose the tests in the format of pytest

name tests using the format test_should{expected result}_given{input data or action} where the words in {} depend on each test


check for coverge after running tests for line coverage greater than 90%

after every passing new test add changed files to git and commit

Commit message generation instructions

undate the documentation instructions before commit

before commiting always check for code duplication and delete duplicated code

before committing changes check if the changed code runs After modifying the code and any other asset provide a short and context specific for generating commit messages

Pull request title and description generation instructions

write a title with a short summary of the mayor changes to the solution

wirte a body describing: What changes were made and significant design decisions made