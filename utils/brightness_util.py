# Import the Windows Management Instrumentation (WMI) module for system control
import wmi

def adjust_brightness(percentage):
    """Adjust the display brightness to the specified percentage
    
    Args:
        percentage (int/str): Desired brightness level (0-100)
        
    Returns:
        str: Success message or error description
        
    Note:
        Requires WMI access and proper display drivers that support brightness control
    """
    try:
        # Convert input to integer to ensure numeric processing
        percentage = int(percentage)
        
        # Validate the brightness percentage is within acceptable range
        if not 0 <= percentage <= 100:
            return f"Error: Brightness percentage must be between 0-100 (got {percentage}%)"
           
        # Initialize WMI connection to the monitor brightness namespace
        c = wmi.WMI(namespace='root\WMI')
        
        # Get the brightness control methods for the first detected monitor
        methods = c.WmiMonitorBrightnessMethods()[0]
        
        # Set the brightness level
        # Parameters:
        # 1. Brightness percentage (0-100)
        # 2. Timeout (0 = immediate change)
        methods.WmiSetBrightness(percentage, 0)
        
        # Return success message with the new brightness level
        return f"Brightness adjusted to {percentage}%"
        
    except Exception as e:
        # Return error message if any step fails
        return f"Error adjusting brightness: {str(e)}"