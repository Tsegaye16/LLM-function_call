import streamlit as st
import json     #for serialization/deserialization

def init_canvas_session():
    """Initialize the canvas session state with default values
    
    Creates and initializes all necessary session state variables
    required for the drawing canvas functionality.
    """
    # Initialize empty list to store drawing objects if not exists
    if 'drawings' not in st.session_state:
        st.session_state.drawings = []
    
    # Set default drawing tool to 'pen' if not exists
    if 'current_tool' not in st.session_state:
        st.session_state.current_tool = 'pen'
    
    # Set default drawing color to red (#FF0000) if not exists
    if 'draw_color' not in st.session_state:
        st.session_state.draw_color = '#FF0000'
    
    # Set default line width to 3 pixels if not exists
    if 'line_width' not in st.session_state:
        st.session_state.line_width = 3

def save_canvas_state():
    """Serialize the current canvas state to JSON string
    
    Returns:
        str: JSON string containing all canvas state information
             including drawings, tool, color and line width
    """
    # Convert current canvas state to JSON format
    return json.dumps({
        'drawings': st.session_state.drawings,        # List of drawing objects
        'current_tool': st.session_state.current_tool,  # Active drawing tool
        'draw_color': st.session_state.draw_color,    # Current drawing color
        'line_width': st.session_state.line_width     # Current line width
    })

def load_canvas_state(state_json):
    """Load canvas state from JSON string
    
    Args:
        state_json (str): JSON string containing saved canvas state
    """
    # Parse JSON string back to Python dictionary
    state = json.loads(state_json)
    
    # Restore drawings from saved state
    st.session_state.drawings = state['drawings']
    
    # Restore drawing tool from saved state
    st.session_state.current_tool = state['current_tool']
    
    # Restore drawing color from saved state
    st.session_state.draw_color = state['draw_color']
    
    # Restore line width from saved state
    st.session_state.line_width = state['line_width']

def clear_canvas():
    """Reset the canvas by clearing all drawings
    
    Maintains current tool, color and line width settings
    but removes all drawing objects from the canvas.
    """
    # Empty the drawings list while keeping other settings
    st.session_state.drawings = []