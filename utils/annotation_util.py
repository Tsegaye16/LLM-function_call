# Import Streamlit library for creating web apps
import streamlit as st
# Import canvas component for drawing functionality
from streamlit_drawable_canvas import st_canvas

def init_annotation_session():
    """Initialize all annotation session variables in Streamlit's session state"""
    
    # Check if annotation tool is set, default to 'freedraw' (pen tool)
    if 'annotation_tool' not in st.session_state:
        st.session_state.annotation_tool = 'freedraw'
    
    # Check if draw color is set, default to red (#FF0000)
    if 'draw_color' not in st.session_state:
        st.session_state.draw_color = '#FF0000'
    
    # Check if stroke width is set, default to 3 pixels
    if 'stroke_width' not in st.session_state:
        st.session_state.stroke_width = 3
    
    # Check if canvas data exists, initialize to None (no existing drawings)
    if 'canvas_data' not in st.session_state:
        st.session_state.canvas_data = None
    
    # Check if canvas key exists (used to force canvas refresh), initialize to 0
    if 'canvas_key' not in st.session_state:
        st.session_state.canvas_key = 0
    

def show_annotation_controls():
    """Display all annotation controls in the Streamlit interface"""
    
    # Ensure all session variables are initialized
    init_annotation_session()
    
    # Create a section header for tools
    st.write("**Tools:**")
    
    # Create 4 columns for tool buttons (we'll use 3 for tools, 1 remains empty)
    cols = st.columns(4)
    
    # Dictionary mapping tool types to their display labels and icons
    tools = {
        'freedraw': '✏️ Pen',       # Freehand drawing tool
        'rect': '⬛ Rectangle',      # Rectangle drawing tool  
        'circle': '⭕ Circle'        # Circle drawing tool
    }
    
    # Create a button for each tool in the columns
    for i, (tool, label) in enumerate(tools.items()):
        with cols[i]:
            # When a tool button is clicked...
            if st.button(label, key=f"tool_{tool}"):
                # Update the current tool in session state
                st.session_state.annotation_tool = tool
                # Note: We don't increment canvas_key here to preserve existing drawings
                # when switching between tools
    
    # Create a section header for appearance settings
    st.write("**Appearance:**")
    
    # Create two columns for color picker and stroke width slider
    col1, col2 = st.columns(2)
    
    with col1:
        # Color picker that updates the drawing color
        st.session_state.draw_color = st.color_picker(
            "Color",                         # Label
            st.session_state.draw_color,     # Current value
            key="color_picker"               # Unique key
        )
    
    with col2:
        # Slider that adjusts the stroke width (1-10 pixels)
        st.session_state.stroke_width = st.slider(
            "Stroke Width",                  # Label
            1, 10,                          # Min, max values
            st.session_state.stroke_width,   # Current value
            key="stroke_slider"              # Unique key
        )

def get_annotation_canvas():
    """Create and return a configured drawing canvas with persistent drawings"""
    
    # Ensure all session variables are initialized
    init_annotation_session()
    
    # Create and return the canvas component with all settings
    return st_canvas(
        # Fill color for shapes (orange with 30% opacity)
        fill_color="rgba(255, 165, 0, 0.3)",
        # Stroke width from session state
        stroke_width=st.session_state.stroke_width,
        # Stroke color from session state
        stroke_color=st.session_state.draw_color,
        # White background
        background_color="#FFFFFF",
        # Fixed canvas dimensions
        height=500,
        width=700,
        # Current drawing mode from session state
        drawing_mode=st.session_state.annotation_tool,
        # Unique key that combines base string with session key
        key=f"canvas_{st.session_state.canvas_key}",
        # Show the toolbar (save, etc.)
        display_toolbar=True,
        # Update Streamlit on changes
        update_streamlit=True,
        # Load any existing drawing data
        initial_drawing=st.session_state.canvas_data
    )