from pdfminer.high_level import extract_text
import re
import json

def extract_text_from_pdf(pdf_file):
    # Extract text from the PDF file
    text = extract_text(pdf_file)
    return text

def extract_questions_from_text(text):
    # Extract questions using a regular expression
    questions = re.findall(r'(\d+)\.\s*(.*?)\n\s*((?:[a-zA-Z]\)\s*.*?\n)+)', text)

    # Create a dictionary to store questions and options
    extracted_questions = {}
    current_question = None
    for question_number, question_text, options_text in questions:
        # If new question, initialize it in the dictionary
        if question_number not in extracted_questions:
            extracted_questions[question_number] = {
                'question': question_text.strip(),
                'options': {},
                'correct_option': None  # Initialize correct_option as None
            }
            current_question = extracted_questions[question_number]
        # Extract options and add them to the current question
        options = re.findall(r'([a-zA-Z])\)\s*(.*?)\n', options_text)
        for option_letter, option_text in options:
            current_question['options'][option_letter.upper()] = option_text.strip()

    return extracted_questions


def format_questions_data(questions):
    # Format the extracted questions and options into JSON format
    formatted_data = {}
    for question_number, question_data in questions.items():
        formatted_data[question_number] = {
            "question": question_data['question'],
            "options": question_data['options'],
            "correct_answer": None  # Set correct answer to null
        }
    return formatted_data

# Upload the PDF file
# uploaded = files.upload()

# Extract text from the uploaded file
# filename = next(iter(uploaded))
# pdf_text = extract_text_from_pdf(filename)
#print(pdf_text)
# Extract questions from the text
# extracted_questions = extract_questions_from_text(pdf_text)

# Format the extracted questions into JSON format
# formatted_data = format_questions_data(extracted_questions)

# Print or save the formatted data as needed
# print(json.dumps(formatted_data, indent=2))