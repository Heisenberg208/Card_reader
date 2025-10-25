import json
import os
from datetime import datetime
from pathlib import Path

import cv2
import easyocr
import numpy as np
import streamlit as st
from google import genai
from google.genai.types import GenerateContentConfig

from utils.constants import RESULTS_FILE


@st.cache_resource(show_spinner=False)
def load_ocr_reader():
    """Load and cache EasyOCR reader safely for Streamlit Cloud"""
    try:

        reader = easyocr.Reader(
            ["en"],
            gpu=False,
            download_enabled=True  # Don't attempt network download
        )
        return reader
    except Exception as e:
        st.error(f"❌ Failed to initialize OCR Reader: {e}")


def resize_image(img, max_dim=1600):
    """Resize business card images for OCR without losing detail"""
    h, w = img.shape[:2]
    scale = max_dim / max(h, w)
    if scale < 1:  # only shrink if it's huge
        img = cv2.resize(
            img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA
        )
    return img


def preprocess_image(image):
    """Preprocess PIL image for better OCR performance"""
    
    # Convert PIL image to NumPy array (OpenCV format)
    img_array = np.array(image)

    # Handle different channel formats
    if img_array.ndim == 2:
        # Already grayscale
        gray = img_array
    elif img_array.shape[2] == 4:
        # RGBA → convert to BGR
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    elif img_array.shape[2] == 3:
        # RGB → convert to BGR → grayscale
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    else:
        raise ValueError(f"Unsupported number of channels: {img_array.shape[2]}")

    # Resize for OCR
    gray = resize_image(gray)  # gray is single channel now

    return gray


def extract_text_from_image(image, reader):
    """Extract text using EasyOCR"""
    processed_img = preprocess_image(image)
    results = reader.readtext(
        processed_img,
        detail=1,
        paragraph=True,
        width_ths=0.7,
        height_ths=0.7,
        batch_size=1,
    )
    extracted_text = "\n".join(
    [r[1] if len(r) > 1 else str(r) for r in results]
)
    return extracted_text.strip() if extracted_text else ""


def clean_and_extract_info(text, api_key):
    """Use Gemini to clean text and extract structured information with guaranteed JSON output"""
    try:
        # Check if API key is valid
        if not api_key or api_key.strip() == "":
            return json.dumps(
                {
                    "error": "Invalid or missing API key",
                    "name": None,
                    "email": None,
                    "phone": None,
                    "company": None,
                    "address": None,
                    "job_title": None,
                    "website": None,
                    "timestamp": datetime.now().isoformat(),
                },
                indent=2,
            )

        # Check if text is valid
        if not text or text.strip() == "":
            return json.dumps(
                {
                    "error": "No text provided for processing",
                    "name": None,
                    "email": None,
                    "phone": None,
                    "company": None,
                    "address": None,
                    "job_title": None,
                    "website": None,
                    "timestamp": datetime.now().isoformat(),
                },
                indent=2,
            )

        client = genai.Client(api_key=api_key)
        prompt = f"""
Analyze the following text extracted from a business card and extract the following information in JSON format:

Text: {text}

Please extract and return ONLY a valid JSON object with these fields:
{{
    "name": ["Full name(s) of the person"],
    "email": ["All email addresses"],
    "phone": ["All phone numbers in normalized international format (+<country code><number>)"],
    "company": "Company Name",
    "address": "complete addresses",
    "job_title": "Job title/position",
    "website": ["All website URLs in normalized format (lowercase, prefixed with 'http://' or 'https://', domain corrected, e.g. 'WWWabc.com' → 'https://www.abc.com')"],
    "timestamp": "{datetime.now().isoformat()}"
}}

Normalization rules:
- Always return values as arrays (e.g., ["value1", "value2"]). If none, return [].
- Phone numbers: Convert all to E.164 international format if possible (+<countrycode><number>), else keep digits only.
- Website: Always lowercase, ensure it starts with 'http://' or 'https://', add 'www.' if missing, fix common mistakes (e.g., 'WWWabc.com' → 'https://www.abc.com').
- If multiple values exist for any field, include them all in the array.
- If a value is missing, return an empty array [].
- Do not include any extra text, explanations, or markdown.
"""

        config = GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=500,
            top_p=0.95,
            top_k=40,
            stop_sequences=["\n\n"],
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp", contents=prompt, config=config
        )

        # Safe response text extraction
        response_text = None

        # Try multiple methods to extract response text
        if hasattr(response, "text") and response.text:
            response_text = response.text
        elif hasattr(response, "candidates") and response.candidates:
            if len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content:
                    if hasattr(candidate.content, "parts") and candidate.content.parts:
                        if len(candidate.content.parts) > 0:
                            response_text = candidate.content.parts[0].text

        # Handle None response
        if response_text is None:
            return json.dumps(
                {
                    "error": "No response text received from Gemini API",
                    "raw_response": str(response),
                    "name": None,
                    "email": None,
                    "phone": None,
                    "company": None,
                    "address": None,
                    "job_title": None,
                    "website": None,
                    "timestamp": datetime.now().isoformat(),
                },
                indent=2,
            )

        # Safe string operations
        response_text = (
            response_text.strip()
            if isinstance(response_text, str)
            else str(response_text).strip()
        )

        # Remove any markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

        # Try to parse the JSON to validate it
        try:
            json_data = json.loads(response_text)
            # Ensure all required fields are present
            required_fields = [
                "name",
                "email",
                "phone",
                "company",
                "address",
                "job_title",
                "website",
            ]
            for field in required_fields:
                if field not in json_data:
                    json_data[field] = None

            # Return properly formatted JSON string
            return json.dumps(json_data, indent=2)
        except json.JSONDecodeError as json_err:
            # If parsing fails, return a valid JSON with error information
            return json.dumps(
                {
                    "error": f"Invalid JSON response from Gemini: {str(json_err)}",
                    "original_response": response_text,
                    "name": None,
                    "email": None,
                    "phone": None,
                    "company": None,
                    "address": None,
                    "job_title": None,
                    "website": None,
                    "timestamp": datetime.now().isoformat(),
                },
                indent=2,
            )

    except Exception as e:
        # Return error information in valid JSON format
        return json.dumps(
            {
                "error": f"Unexpected error: {str(e)}",
                "error_type": type(e).__name__,
                "name": None,
                "email": None,
                "phone": None,
                "company": None,
                "address": None,
                "job_title": None,
                "website": None,
                "timestamp": datetime.now().isoformat(),
            },
            indent=2,
        )


def process_ocr_to_json(image, reader, api_key):
    """One-click function to extract text from image and convert to JSON"""
    try:
        # Validate API key first
        if not api_key or api_key.strip() == "":
            return (
                json.dumps(
                    {
                        "error": "Invalid or missing Gemini API key",
                        "name": None,
                        "email": None,
                        "phone": None,
                        "company": None,
                        "address": None,
                        "job_title": None,
                        "website": None,
                        "timestamp": datetime.now().isoformat(),
                    },
                    indent=2,
                ),
                "",
            )

        # Step 1: Extract text using OCR
        extracted_text = extract_text_from_image(image, reader)

        if not extracted_text:
            return (
                json.dumps(
                    {
                        "error": "No text was extracted from the image",
                        "name": None,
                        "email": None,
                        "phone": None,
                        "company": None,
                        "address": None,
                        "job_title": None,
                        "website": None,
                        "timestamp": datetime.now().isoformat(),
                    },
                    indent=2,
                ),
                "",
            )

        # Step 2: Process with Gemini AI
        json_result = clean_and_extract_info(extracted_text, api_key)

        return json_result, extracted_text

    except Exception as e:
        return (
            json.dumps(
                {
                    "error": f"Processing error: {str(e)}",
                    "error_type": type(e).__name__,
                    "name": None,
                    "email": None,
                    "phone": None,
                    "company": None,
                    "address": None,
                    "job_title": None,
                    "website": None,
                    "timestamp": datetime.now().isoformat(),
                },
                indent=2,
            ),
            "",
        )


def save_to_json(data):
    """Save or append data to JSON file"""
    try:
        # Try to load existing data
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        # Append new data
        existing_data.append(data)

        # Save back to file
        with open(RESULTS_FILE, "w") as f:
            json.dump(existing_data, f, indent=2)

        return True
    except Exception as e:
        st.error(f"Error saving to JSON file: {str(e)}")
        return False
