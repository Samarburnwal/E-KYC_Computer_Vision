import pandas as pd
from datetime import datetime
import json

def filter_lines(lines):
    start_index = None
    end_index = None

    # Find start and end indices
    for i, line in enumerate(lines):
        if "INCOME TAX DEPARTMENT" in line:
            start_index = i
        if "Signature" in line:
            end_index = i
            break

    # Filter lines based on conditions
    filtered_lines = []
    if start_index is not None and end_index is not None:
        for line in lines[start_index:end_index + 1]:
            if len(line.strip()) > 2:
                filtered_lines.append(line.strip())
    
    return filtered_lines

def create_dataframe(texts):

    lines = filter_lines(texts)
    print("="*20)
    print(lines)
    print("="*20)
    data = []
    name = lines[2].strip()
    father_name = lines[3].strip()
    dob = lines[4].strip()
    for i in range(len(lines)):
        if "Permanent Account Number" in lines[i]:
            pan = lines[i+1].strip()
    data.append({"ID": pan, "Name": name, "Father's Name": father_name, "DOB": dob, "ID Type": "PAN"})
    df = pd.DataFrame(data)
    return df


import re

def normalize_digits(text):
    # Convert Hindi numerals to English (if any)
    devanagari_nums = '०१२३४५६७८९'
    english_nums = '0123456789'
    return text.translate(str.maketrans(devanagari_nums, english_nums))

def extract_clean_fields(raw_text):
    text = normalize_digits(raw_text)
    
    # Extract Name (first proper capitalized name with 2+ words)
    name_match = re.search(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\b', text)
    name = name_match.group(1) if name_match else None

    # Extract DOB
    dob_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
    dob = dob_match.group() if dob_match else None

    # Extract Gender
    if 'MALE' in text:
        gender = 'MALE'
    elif 'FEMALE' in text:
        gender = 'FEMALE'
    else:
        gender = None

    # Extract Aadhaar number (12-digit format: xxxx xxxx xxxx)
    aadhaar_match = re.search(r'\b\d{4}[\s\-\.]?\d{4}[\s\-\.]?\d{4}\b', text)
    aadhaar = aadhaar_match.group().replace('-', ' ').replace('.', ' ') if aadhaar_match else None

    return {
        'Name': name,
        'DOB': dob,
        'Gender': gender,
        'Aadhaar': aadhaar
    }

def truncate_from_vid(text):
    keyword = "VID"
    if keyword in text:
        return text.split(keyword)[0].strip()  # remove everything from VID onwards
    return text.strip()  # return original if VID not found


def extract_information(data_string):
    # Split the data string into a list of words based on "|"
    updated_data_string = data_string.replace(".", "")
    words = [word.strip() for word in updated_data_string.split("|") if len(word.strip()) > 2]
    data_string = normalize_digits(data_string)
    data_string = truncate_from_vid(data_string)
    print(data_string)

    # Initialize the dictionary to store the extracted information
    return extract_clean_fields(data_string)