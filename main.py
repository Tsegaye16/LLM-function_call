# Import necessary libraries
import pandas as pd
import streamlit as st  # For building the web app interface
import google.generativeai as genai  # For accessing Gemini AI
from utils.audio_util import adjust_volume  # Volume control utility
from utils.brightness_util import adjust_brightness  # Screen brightness control
from utils.distance_util import get_distance  # Distance calculation utility
from utils.file_analysis_util import group_related_files  # File grouping utility
from utils.media_util import open_first_media_file, navigate_media_file  # Media file handling
from utils.db_util import query_telegram_messages  # Database query utility
from config import GOOGLE_API_KEY  # API key configuration
from utils.annotation_util import *  # Annotation tools
from utils.canvas_util import *  # Canvas drawing utilities
import comtypes  # For COM object initialization (Windows specific)
import time  # For time-related functions
from streamlit_drawable_canvas import st_canvas  # Interactive canvas component
from utils.tts_util import read_file_aloud  # Text-to-speech functionality

# Initialize COM (Component Object Model) for Windows applications
comtypes.CoInitialize()

# Configure Gemini API with the provided API key
genai.configure(api_key=GOOGLE_API_KEY)
# Initialize the Gemini model with flash version
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to load custom CSS styles
def load_css():
    """Loads custom CSS styles from styles.css file"""
    with open("styles.css") as f:
        # Inject CSS into the Streamlit app
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS styles
load_css()

def handle_markdown_command(text):
    """Processes markdown commands in user input"""
    if "```markdown" in text:
        # Extract markdown content between the markers
        md_content = text.split("```markdown")[1].split("```")[0]
        return "Here's your rendered markdown:", md_content
    return None, None

# Initialize chat history and session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []  # Stores chat messages

if "current_file_index" not in st.session_state:
    st.session_state.current_file_index = 0  # Tracks current media file index

if "file_list" not in st.session_state:
    st.session_state.file_list = []  # Stores list of media files

if "whiteboard_mode" not in st.session_state:
    st.session_state.whiteboard_mode = False  # Whiteboard toggle state

if "presentation_mode" not in st.session_state:
    st.session_state.presentation_mode = False  # Presentation mode state

# Display existing chat messages
for message in st.session_state.messages:
    # Set avatar based on message role
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])  # Display message content

# Chat input field
if prompt := st.chat_input("Type your message..."):
    # First check for markdown commands
    md_response = handle_markdown_command(prompt)
    if md_response[0]:
        # Add markdown response to chat history
        st.session_state.messages.append({"role": "assistant", "content": md_response[0]})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(md_response[1])  # Render the markdown
    else:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)  # Display user message

        # Start chat with Gemini AI
        chat = model.start_chat(history=[])
        # Send prompt with all available tools/functionalities
        response = chat.send_message(
            prompt,
            tools=[{
                "function_declarations": [
                    # Brightness adjustment tool
                    {
                        "name": "adjust_brightness",
                        "description": "Adjusts screen brightness percentage",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "percentage": {
                                    "type": "NUMBER",
                                    "description": "Brightness percentage (0-100)",
                                },
                            },
                            "required": ["percentage"],
                        },
                    },
                    # Volume adjustment tool
                    {
                        "name": "adjust_volume",
                        "description": "Adjusts system volume percentage",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "percentage": {
                                    "type": "NUMBER",
                                    "description": "Volume percentage (0-100)",
                                },
                            },
                            "required": ["percentage"],
                        },
                    },
                    # Distance calculation tool
                    {
                        "name": "get_distance",
                        "description": "Calculates driving distance between locations",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "origin": {"type": "STRING", "description": "Start location"},
                                "destination": {"type": "STRING", "description": "End location"},
                            },
                            "required": ["origin", "destination"],
                        },
                    },
                    # Media file opener
                    {
                        "name": "open_first_media_file",
                        "description": "Opens first media file in folder",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "folder_path": {
                                    "type": "STRING",
                                    "description": "Path to media files folder",
                                },
                            },
                            "required": ["folder_path"],
                        },
                    },
                    # Media file navigator
                    {
                        "name": "navigate_media_file",
                        "description": "Navigates between media files",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "direction": {
                                    "type": "STRING",
                                    "enum": ["next", "previous"],
                                    "description": "Navigation direction",
                                },
                            },
                            "required": ["direction"],
                        },
                    },
                    # Telegram messages query
                    {
                        "name": "query_telegram_messages",
                        "description": "Queries telegram messages database",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "query": {
                                    "type": "STRING",
                                    "description": "Search query",
                                },
                            },
                            "required": ["query"],
                        },
                    },
                    # Annotation tool starter
                    {
                        "name": "start_annotation",
                        "description": "Starts annotation with specified tool",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "tool": {
                                    "type": "STRING",
                                    "enum": ["pen", "rectangle", "circle"],
                                    "description": "Annotation tool to use",
                                },
                            },
                            "required": ["tool"],
                        },
                    },                    
                    # Whiteboard toggle
                    {
                        "name": "toggle_whiteboard",
                        "description": "Toggles whiteboard mode",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "enable": {
                                    "type": "BOOLEAN",
                                    "description": "Enable/disable whiteboard",
                                },
                            },
                            "required": ["enable"],
                        },
                    },
                    # Text-to-speech reader
                    {
                        "name": "read_file_aloud",
                        "description": "Reads file content aloud",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "file_path": {
                                    "type": "STRING",
                                    "description": "Path to file to read",
                                },
                            },
                            "required": ["file_path"],
                        },
                    },
                    # File grouping tool
                    {
                        "name": "group_related_files",
                        "description": "Groups similar files in folder",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "folder_path": {
                                    "type": "STRING",
                                    "description": "Path to folder to analyze",
                                },
                                "output_folder": {
                                    "type": "STRING",
                                    "description": "Output folder name",
                                },
                                "similarity_threshold": {
                                    "type": "NUMBER",
                                    "description": "Similarity threshold (0-1)",
                                },
                            },
                            "required": ["folder_path"],
                        },
                    }                
                ]
            }]
        )

        # Process Gemini's response
        if hasattr(response.parts[0], 'function_call') and response.parts[0].function_call:
            function_name = response.parts[0].function_call.name
            arguments = response.parts[0].function_call.args

            # Brightness adjustment handler
            if function_name == "adjust_brightness":
                percentage = arguments.get("percentage")
                if percentage is not None:
                    function_result = adjust_brightness(percentage)
                    st.session_state.messages.append({"role": "assistant", "content": function_result})
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(function_result)

            # Volume adjustment handler
            elif function_name == "adjust_volume":
                percentage = arguments.get("percentage")
                if percentage is not None:
                    function_result = adjust_volume(percentage)
                    st.session_state.messages.append({"role": "assistant", "content": function_result})
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(function_result)

            # Distance calculation handler
            elif function_name == "get_distance":
                origin = arguments.get("origin")
                destination = arguments.get("destination")
                if origin and destination:
                    function_result = get_distance(origin, destination)
                    st.session_state.messages.append({"role": "assistant", "content": function_result})
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(function_result)

            # Media file opener handler
            elif function_name == "open_first_media_file":
                folder_path = arguments.get("folder_path")
                if folder_path:
                    result = open_first_media_file(folder_path)
                    st.session_state.messages.append({"role": "assistant", "content": result["message"]})
                    if result["status"] == "success":
                        st.session_state.current_file_index = result["current_file_index"]
                        st.session_state.file_list = result["file_list"]
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(result["message"])

            # Media file navigation handler
            elif function_name == "navigate_media_file":
                direction = arguments.get("direction")
                if direction:
                    result = navigate_media_file(
                        direction,
                        st.session_state.current_file_index,
                        st.session_state.file_list
                    )
                    st.session_state.messages.append({"role": "assistant", "content": result["message"]})
                    if result["status"] == "success":
                        st.session_state.current_file_index = result["current_file_index"]
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(result["message"])

            # Telegram messages query handler
            if function_name == "query_telegram_messages":
                query = arguments.get("query")
                if query:
                    result = query_telegram_messages(query)
                    if result["status"] == "success":
                        if "data" in result:
                            # Convert the data to a pandas DataFrame for easy tabular display
                            df = pd.DataFrame(result["data"], columns=["ID", "Channel", "Message ID", "Message", "Timestamp", "Media", "Emojis", "URL", "Metadata"])
                            st.session_state.messages.append({"role": "assistant", "content": "Here are the results in a table format:"})
                            with st.chat_message("assistant", avatar="🤖"):
                                st.markdown("Here are the results in a table format:")
                                st.dataframe(df)  # Display the DataFrame as a table
                        else:
                            st.session_state.messages.append({"role": "assistant", "content": result["message"]})
                            with st.chat_message("assistant", avatar="🤖"):
                                st.markdown(result["message"])
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": result["message"]})
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(result["message"])

            # Annotation tool starter handler
            elif function_name == "start_annotation":
                tool = arguments.get("tool", "pen")
                tool_mapping = {
                    "pen": "freedraw",
                    "rectangle": "rect", 
                    "circle": "circle"
                }
                
                init_annotation_session()
                st.session_state.annotation_tool = tool_mapping.get(tool, "freedraw")
                st.session_state.whiteboard_mode = True
                
                response_msg = f"🎨 Whiteboard: {tool} tool active"
                st.session_state.messages.append({"role": "assistant", "content": response_msg})
                
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(response_msg)
                    show_annotation_controls()
                    canvas = get_annotation_canvas()
                    
                    if canvas.json_data is not None:
                        st.session_state.canvas_data = canvas.json_data

            # Whiteboard toggle handler
            elif function_name == "toggle_whiteboard":
                enable = arguments.get("enable", True)
                st.session_state.whiteboard_mode = enable
                response_msg = "🖍️ Whiteboard enabled" if enable else "Whiteboard disabled"
                st.session_state.messages.append({"role": "assistant", "content": response_msg})
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(response_msg)  
            
            # Text-to-speech handler
            elif function_name == "read_file_aloud":
                file_path = arguments.get("file_path")
                if file_path:
                    result = read_file_aloud(file_path)
                    st.session_state.messages.append({"role": "assistant", "content": result["message"]})
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(result["message"])    
            
            # File grouping handler
            elif function_name == "group_related_files":
                folder_path = arguments.get("folder_path")
                output_folder = arguments.get("output_folder", "grouped_files")
                similarity_threshold = arguments.get("similarity_threshold", 0.5)
                
                result = group_related_files(folder_path, output_folder, similarity_threshold)
                
                if result["status"] == "success":
                    response_msg = (f"✅ Successfully grouped files into {len(result['groups'])} groups.\n"
                                f"📁 Output folder: {result['output_folder']}\n\n"
                                "Groups created:\n" + 
                                "\n".join([f"- {g['group_name']}: {', '.join(g['files'])}" 
                                        for g in result["groups"]]))
                else:
                    response_msg = f"❌ Error: {result['message']}"
                
                st.session_state.messages.append({"role": "assistant", "content": response_msg})
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(response_msg)    
       
        # If no function call, just display Gemini's text response
        else:
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(response.text)

# Display whiteboard if enabled
if st.session_state.get('whiteboard_mode', False):
    st.subheader("🖍️ Interactive Whiteboard")
    show_annotation_controls()
    canvas = get_annotation_canvas()
    
    if canvas.json_data is not None:
        st.session_state.canvas_data = canvas.json_data