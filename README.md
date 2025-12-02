# Quest 3 OpenXR Streamer

A modular Python application to stream real-time controller data (pose, velocity, and inputs) from a Meta Quest 3 headset to a Linux PC using OpenXR and WiVRn.

## Features

*   **Real-time Tracking**: Captures Head, Left/Right Controller Aim, and Grip poses.
*   **Velocity Data**: Streams Linear and Angular velocity for controllers.
*   **Input Capture**: Reads Trigger, Squeeze, and Button states (A/B/X/Y, Menu, Thumbstick).
*   **Modular Design**: Cleanly separated into graphics, core OpenXR, and input management modules.
*   **OpenGL Backend**: Uses a hidden GLFW window to satisfy OpenXR session requirements on Linux.

## Prerequisites

### Hardware
*   Meta Quest 3 (or compatible OpenXR headset).
*   Linux PC (tested on Ubuntu/Debian).
*   5GHz Wi-Fi router (for wireless streaming via WiVRn).

### Software
*   **WiVRn**: An open-source OpenXR streaming runtime. Ensure the server is running on your PC and the client is installed on your headset.
*   **Python 3.8+**

## Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/YOUR_USERNAME/quest3-openxr-streamer.git
    cd quest3-openxr-streamer
    ```

2.  **Create a Virtual Environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install pyopenxr glfw PyOpenGL
    ```

4.  **System Dependencies**
    Ensure you have GLFW and GLX libraries installed:
    ```bash
    sudo apt-get install libglfw3 libgl1-mesa-glx
    ```

## Usage

1.  **Start WiVRn Server**
    Ensure your headset is connected to WiVRn.

2.  **Run the Streamer**
    Execute the main script. You may need to force the X11 backend for GLFW if you are on Wayland (common with WiVRn).

    ```bash
    # For X11 / Standard Setup
    python quest_stream_opengl.py

    # If you encounter windowing issues or are on Wayland:
    WAYLAND_DISPLAY= XDG_SESSION_TYPE=x11 python quest_stream_opengl.py
    ```

3.  **Interact**
    *   Put on the headset.
    *   The script will wait for the session to become focused.
    *   Once focused, you will see real-time data streaming in your terminal.

## Troubleshooting

*   **"Session not focused"**: Make sure you are wearing the headset and the WiVRn application is active.
*   **"Could not load libGL.so.1"**: Install `libgl1-mesa-glx`.
*   **"Failed to init GLFW"**: Ensure you are running in a graphical environment (not a pure TTY).

## License

MIT License
