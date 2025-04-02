# Standard library imports
import os          # For operating system path operations
import glob        # For file pattern matching
import subprocess  # For launching external applications

def open_first_media_file(folder_path):
    """Opens the first media file (MP3/MP4) found in the specified folder.
    
    Args:
        folder_path (str): Path to the folder containing media files
        
    Returns:
        dict: Dictionary containing:
            - status: "success" or "error"
            - message: Result description
            - current_file_index: Index of opened file (0 if success)
            - file_list: List of all matching files (empty if error)
    """
    try:
        # Verify the folder exists
        if not os.path.exists(folder_path):
            return f"Error: Folder '{folder_path}' does not exist."

        # Find all MP3 and MP4 files in the folder
        files = glob.glob(os.path.join(folder_path, '*.mp3')) + \
                glob.glob(os.path.join(folder_path, '*.mp4'))
        
        if files:
            # Get the first file in the list
            file_path = files[0]
            
            # Open the file using the default system application
            subprocess.Popen([file_path], shell=True)
            
            return {
                "status": "success",
                "message": f"Opened file: {file_path}",
                "current_file_index": 0,  # Track position in playlist
                "file_list": files       # Store full list for navigation
            }
        else:
            return {
                "status": "error",
                "message": f"No MP3 or MP4 files found in folder: {folder_path}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error opening file: {str(e)}"
        }

def navigate_media_file(direction, current_index, file_list):
    """Navigates to next/previous media file in a playlist.
    
    Args:
        direction (str): "next" or "previous"
        current_index (int): Current position in file_list
        file_list (list): List of media file paths
        
    Returns:
        dict: Dictionary containing:
            - status: "success" or "error"
            - message: Result description
            - current_file_index: New position in playlist
            - file_list: Original file list (for chaining)
    """
    try:
        # Check if there are files to navigate
        if not file_list:
            return {
                "status": "error",
                "message": "No files are currently open."
            }

        # Calculate new index based on direction
        if direction == "next":
            new_index = (current_index + 1) % len(file_list)  # Wrap around
        elif direction == "previous":
            new_index = (current_index - 1) % len(file_list)  # Wrap around
        else:
            return {
                "status": "error",
                "message": "Invalid navigation direction."
            }

        # Get and open the new file
        new_file_path = file_list[new_index]
        subprocess.Popen([new_file_path], shell=True)

        return {
            "status": "success",
            "message": f"Opened file: {new_file_path}",
            "current_file_index": new_index,
            "file_list": file_list  # Return original list for consistency
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error navigating files: {str(e)}"
        }