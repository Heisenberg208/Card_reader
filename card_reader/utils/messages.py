# General Header and Descriptions

# streamlit_app.py messages
TITLE_YOLO = "✨:blue[Fabric Generator ]"
TITLE_FABRIC = "✨:blue[Fabric Descriptor ]"
TITLE_OCR = "✨:blue[Business Card Reader]"

DESCRIPTION_YOLO = (
    "This application utilizes object detection to identify multiple fabric patterns in your uploaded "
    "images. When you upload a single image and a group image, the system detects individual fabrics within the group. "
    "Based on the dominant colors of the detected fabrics, it generates visually appealing color variations of single fabric image."
)
DESCRIPTION_FABRIC = (
    "The Fabric Description App uses Google's Gemini API to analyze fabric images and provide detailed, AI-generated "
    "descriptions.Just upload a fabric photo or enter its name to get insights on texture, material, pattern, and usage. Ideal for designers, sellers, and students "
    "in textiles. Fast, accurate, and easy to use with multimodal AI."
)
DESCRIPTION_OCR = (
    " Business Card OCR is a smart document processing application that automatically extracts and structures contact information from business card images. Users can either "
    "upload their own business card photos or select from sample images, then leverage OCR technology to extract text which is further processed by AI to organize the information "
    "into structured JSON format."
)

DESCRIPTION_SEARCH = (
    "A smart fabric search app powered by SigLIP and LanceDB enables users to find similar textiles using images or descriptions. SigLIP converts "
    "fabric visuals and text into rich embeddings for accurate similarity search. LanceDB provides fast, scalable vector search to quickly retrieve matching fabrics from large catalogs. "
    "This app enhances product discovery for designers, retailers, and manufacturers."
)


# Specific Messages for Image Generation
SINGLE_IMAGE = ":green[Single image]"
GROUP_IMAGE = ":green[Group image]"

SINGLE_IMAGE_LABEL = "Upload a single image with a clear visible pattern."


GROUP_IMAGE_LABEL = (
    "Upload a group image which has all color variations of the first image."
)


FOOTER_HTML = """<style>
a:link , a:visited{
color: #666;
text-decoration: underline;
transition: all 0.3s ease;
}

a:hover,  a:active {
color: #ff4444;
background-color: transparent;
text-decoration: underline;
transform: translateY(-1px);
}

.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-align: center;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0.25rem 0;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.15);
    border-top: 1px solid #ffffff20;
    backdrop-filter: blur(10px);
    z-index: 1000;
    height: 35px;
}

.footer p {
    margin: 0;
    font-size: 14px;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.footer a {
    color: #ffffff !important;
    font-weight: 600;
    text-decoration: none;
    border-bottom: 2px solid transparent;
    padding: 2px 4px;
    border-radius: 3px;
  }

.footer a:hover {
    color: #ffeb3b !important;
    border-bottom: 2px solid #ffeb3b;
    background: rgba(255, 255, 255, 0.1);
  }

</style>
<div class="footer">
<p>Developed with ❤ by <a style='display: inline' href="https://www.recursivezero.com/" target="_blank">RecursiveZero</a></p>
</div>
"""

# Table_messages(make_table.py)
info_start_connecting = "Connecting to the database..."
info_scanning_directory = "Scanning directory: {root_folder}"
info_found_images = "Found {count} images in the root folder."
error_no_images_found = "No images found in the specified directory."
info_table_exists = "Table doesn't exist."
info_creating_table = "Creating new table '{table_name}'..."
info_adding_images = "Adding {count} images to the table."
info_successfully_added = "Successfully added images to the table."
warning_no_images_found = "No images found to add to the table."
info_checking_for_duplicates = "Checking for duplicates in the table..."
error_required_columns = "Required columns not found. Skipping deduplication."
info_no_duplicates_found = "No duplicates found in the table."
info_removed_duplicates = "Successfully removed duplicate entries."
info_added_new_modified_images = "Added {count} new or modified images."
info_removed_missing_images = "Removed {count} missing images."
info_dropping_existing_table = "Force flag set. Dropping existing table '{table_name}'."
info_updating_table = "Updating existing table '{table_name}'..."
info_final_table_preview = "Final table preview:"

# Search_UI.py messages
# General Messages
PAGE_TITLE = "✨:blue[Fabric Search]"
NO_IMAGES_FOUND = "No images found."
TABLE_UPDATE_SUCCESS = "Table updated successfully!"
TABLE_UPDATE_ERROR = "Error updating table: {error}"
SEARCH_COMPLETED_SUCCESS = "Search completed successfully!"
NO_IMAGES_FOUND_QUERY = "No images found for the search query."
ERROR_DURING_SEARCH = "Error during search: {error}"
DISPLAYED_IMAGES_COUNT = "Showing {currently_showing} of {total_images} images"

# Form Labels and Help Text

UPLOAD_HELP_TEXT = "Upload an image to use as a search query."
SEARCH_QUERY_PLACEHOLDER = "Enter search terms ex:Blue,White,Floral "
SEARCH_QUERY_HELP_TEXT = "Enter a text query to search for images."
LIMIT_HELP_TEXT = "Set the maximum number of results to return. Use 0 for no limit."
FORCE_UPDATE_HELP_TEXT = (
    "Force update creates a new table from images deleting the old one"
)
NO_INPUT = "No input provided. Please upload an image or enter a search query."
RUN_SEARCH_BUTTON_HELP = "Initiate search with current parameters."
CLEAR_BUTTON_HELP = "Reset search results."
UPDATE_TABLE_BUTTON_HELP = "Update or create database table."

# ROUTE_AWS.py MESSAGES

UPLOAD_SUCCESS_S3 = "File uploaded successfully to S3 Bucket."

UPLOAD_HELP_TEXT = "Upload an image to use as a search query."


SEARCH_SETTINGS_SUBHEADER = ":green[Search Settings]"


S3_UPLOAD_FAILURE = "Failed to upload file to S3."
S3_INVALID_PARAMETERS = "Object key and bucket name cannot be empty."
S3_PRESIGNED_URL_FAILURE = "Error generating pre-signed URL."


# Audio_recorder.py messages
APP_TITLE = ":green[Audio Recorder]"
APP_DESCRIPTION = "Please record the details of the product within one limit (Maximum 60 seconds can be recorded)"

# Save audio file messages
SAVE_AUDIO_BUTTON_TEXT = "Save Audio File"
FILENAME_INPUT_PROMPT = "Enter the name for the audio file (without extension):"
FILENAME_WARNING = "Please enter a filename."
AUDIO_SAVED_MESSAGE = "Audio file saved as: {}"

# Description
DESCRIPTION_HTML = """
    <style>
        .description-box {
            background-color: #5353e2;
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #1f4e79;
            margin: 1rem 0;
        }
        .analysis-section {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            background-color: #fafafa;
        }
        .header-link {
            color: #1f4e79;
            text-decoration: none;
            font-weight: 500;
            cursor: pointer;
        }
        .header-link:hover {
            text-decoration: underline;
        }
        .small-sample-btn {
            font-size: 0.8rem !important;
            padding: 0.25rem 0.5rem !important;
            height: auto !important;
            min-height: 2rem !important;
        }
        .analysis-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }
        
    """
DESCRIPTION_SAMPLE_HTML = """
    <style>
    .sample-card {
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .sample-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1f4e79;
        margin: 10px 0;
        text-align: center;
    }
    
    .fabric-preview {
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 10px auto;
        display: block;
    }
    
    .dialog-header {
        text-align: center;
        color: #1f4e79;
        font-size: 1.3rem;
        margin-bottom: 20px;
        font-weight: 600;
    }
    </style>
    """
DESCRIPTION_CHAT_HTML = """
    <style>
    .user-message {
        background-color: black;
        color: white;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        margin-left: 50px;
        position: relative;
    }
    
    .user-message:before {
        content: "👤";
        position: absolute;
        left: -35px;
        top: 15px;
        font-size: 20px;
    }
    
    .assistant-message {
        background-color: #9c4dc4;
        color: white;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        margin-right: 50px;
        position: relative;
    }
    
    .assistant-message:before {
        content: "🤖";
        position: absolute;
        right: -35px;
        top: 15px;
        font-size: 20px;
    }
    
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        background-color: #fafafa;
    }
    </style>
    """
