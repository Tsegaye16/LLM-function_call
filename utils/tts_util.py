import pyttsx3      # for text-to-speech functionality
import os 
from PyPDF2 import PdfReader    # for PDF text extraction

def read_file_aloud(file_path):
    """Reads the contents of a text or PDF file aloud using text-to-speech.
    
    Args:
        file_path (str): Path to the file to be read
        
    Returns:
        dict: Dictionary containing:
            - status: "success" or "error"
            - message: Detailed result message
    
    Supported Formats:
        - PDF (.pdf)
        - Text (.txt, .md)
        - Data files (.csv, .json)
    """
    try:
        # Check if the specified file exists at the given path
        if not os.path.exists(file_path):
            return {
                "status": "error", 
                "message": f"File not found: {file_path}"
            }
        
        # Initialize the text-to-speech engine
        engine = pyttsx3.init()
        
        # Handle PDF file format
        if file_path.lower().endswith('.pdf'):
            # Create PDF reader object
            pdf_reader = PdfReader(file_path)
            text = ""
            
            # Extract text from each page
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Check if any text was extracted
            if not text.strip():
                return {
                    "status": "error", 
                    "message": "No readable text found in PDF"
                }
            
            # Convert text to speech
            engine.say(text)
            engine.runAndWait()
            
            return {
                "status": "success", 
                "message": f"Finished reading PDF: {os.path.basename(file_path)}"
            }
        
        # Handle text-based file formats
        elif file_path.lower().endswith(('.txt', '.md', '.csv', '.json')):
            # Read file content with UTF-8 encoding
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Convert text to speech
            engine.say(content)
            engine.runAndWait()
            
            return {
                "status": "success", 
                "message": f"Finished reading: {os.path.basename(file_path)}"
            }
        
        # Handle unsupported file formats
        else:
            return {
                "status": "error", 
                "message": "Unsupported file format"
            }
    
    # Handle any exceptions that occur during processing
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Error reading file: {str(e)}"
        }