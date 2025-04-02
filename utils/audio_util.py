
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume   # for audio control
from ctypes import cast, POINTER    # for pointer casting
from comtypes import CLSCTX_ALL

def get_volume_interface():
    """Initialize and return the audio volume control interface
    
    Returns:
        Pointer to IAudioEndpointVolume interface
        
    Raises:
        Exception: If audio interface initialization fails
    """
    try:
        # Get the default audio playback device (speakers)
        devices = AudioUtilities.GetSpeakers()
        
        # Activate the volume control interface
        interface = devices.Activate(
            IAudioEndpointVolume._iid_,  # Interface ID for volume control
            CLSCTX_ALL,                 # Context for all COM objects
            None                        # Optional parameters
        )
        
        # Cast the interface to the correct pointer type and return
        return cast(interface, POINTER(IAudioEndpointVolume))
        
    except Exception as e:
        # Wrap any errors in a more descriptive exception
        raise Exception(f"Error initializing audio interface: {str(e)}")

def adjust_volume(percentage):
    """Adjust system volume to the specified percentage
    
    Args:
        percentage (int/float): Desired volume level (0-100)
        
    Returns:
        str: Success message or error description
    """
    try:
        # Get the volume control interface
        volume_interface = get_volume_interface()
        
        # Check if interface was obtained successfully
        if volume_interface is None:
            return "Error: Could not access volume controls"
           
        # Convert percentage to float for safety
        percentage = float(percentage)
        
        # Validate percentage range
        if not 0 <= percentage <= 100:
            return f"Error: Volume percentage must be between 0-100 (got {percentage}%)"
       
        # Convert percentage to scalar value (0.0-1.0)
        scalar = percentage / 100.0
        
        # Set the system volume
        volume_interface.SetMasterVolumeLevelScalar(
            scalar,  # Volume level (0.0-1.0)
            None     # Optional context (unused)
        )
        
        # Return success message
        return f"Volume adjusted to {percentage}%"
        
    except Exception as e:
        # Return any errors that occurred
        return f"Error adjusting volume: {str(e)}"