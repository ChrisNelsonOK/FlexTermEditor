"""
Utility functions for the text editor
"""

import os
import platform
import shutil

def get_available_shells():
    """Get a list of available shells on the current system"""
    available_shells = []
    
    if platform.system() == "Windows":
        # Windows always has cmd.exe
        available_shells.append("cmd")
        
        # Check for PowerShell
        if shutil.which("powershell.exe"):
            available_shells.append("powershell")
        
        # Check for Git Bash or similar
        if shutil.which("bash.exe"):
            available_shells.append("bash")
    else:
        # Unix-like systems
        shell_paths = [
            ("/bin/bash", "bash"),
            ("/bin/zsh", "zsh"),
            ("/bin/sh", "sh"),
            ("/bin/fish", "fish")
        ]
        
        for path, name in shell_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                available_shells.append(name)
    
    # Ensure there's at least one shell available
    if not available_shells:
        if platform.system() == "Windows":
            available_shells.append("cmd")  # Fallback for Windows
        else:
            available_shells.append("sh")   # Fallback for Unix-like
    
    return available_shells

def get_file_extension(filename):
    """Get the extension of a file"""
    if not filename:
        return ""
    
    _, ext = os.path.splitext(filename)
    return ext.lower()
