import re
from docx import Document
import json

# Regular expressions to extract information
module_number_pattern = re.compile(r" (\S+)")
module_name_pattern = re.compile(r"Module name (.+)")
contents_pattern = re.compile(r"Qualification goalsContents:(.+?)(?:Qualification goals|$)", re.DOTALL)
credit_points_pattern = re.compile(r"Credit points and grades (\d+)")

# Function to extract information from a page
def extract_information(page_text):
    result = {}

    # Extract Module Number
    match_module_number = module_number_pattern.search(page_text)
    if match_module_number:
        result["Module number"] = match_module_number.group(1)

    # Extract Module Name
    match_module_name = module_name_pattern.search(page_text)
    if match_module_name:
        result["Module name"] = match_module_name.group(1)

    # Extract Contents
    match_contents = contents_pattern.search(page_text)
    if match_contents:
        contents = match_contents.group(1).strip()
        # Remove unwanted characters
        contents = contents.replace('\u2022', '').replace('\n', '')
        result["Content and Qualification goalsContents"] = contents

    # Extract Credit Points
    match_credit_points = credit_points_pattern.search(page_text)
    if match_credit_points:
        result["Credit points"] = match_credit_points.group(1)

    return result

# Function to read text from a Word document
def read_text_from_word(word_path):
    doc = Document(word_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Example Word document path (replace this with your actual Word file path)
input_word_path = "output.docx"

# Read text from the Word document
word_text = read_text_from_word(input_word_path)

# Split the text into pages
pages = re.split(r"Module number", word_text)[1:]

# Extract information from each page
result_list = [extract_information(page) for page in pages]

# Convert the list of dictionaries to JSON
json_data = json.dumps(result_list, indent=2)

# Write JSON data to a separate file
output_json_path = "output.json"
with open(output_json_path, "w") as json_file:
    json_file.write(json_data)

print(f"JSON data has been written to {output_json_path}")
