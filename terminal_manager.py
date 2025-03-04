"""
Terminal Manager - Handles shell command execution and output management
"""

import os
import platform
import pexpect
import subprocess
import sys
import time
# Handle different versions of prompt_toolkit
try:
    # For prompt_toolkit 3.x (the recommended way)
    from prompt_toolkit.formatted_text import FormattedText
except ImportError:
    try:
        # For prompt_toolkit 2.x
        from prompt_toolkit.formatted_text.base import FormattedText
    except ImportError:
        # Fallback implementation if import fails
        # Define our own FormattedText class for when prompt_toolkit is not available
        class FormattedText(list):
            """Simple fallback implementation of FormattedText"""
            pass

# Define common prompt pattern for shells
SHELL_PROMPT_PATTERN = r'[$#>] '

class TerminalManager:
    """Manages shell processes and command execution"""
    
    def __init__(self, shell_type=None):
        """Initialize the terminal manager with the specified shell"""
        self.shell_type = shell_type or self._get_default_shell()
        self.command_history = []
        self.output_history = []
        self._spawn_shell()
    
    def _get_default_shell(self):
        """Get the default shell for the current system"""
        if platform.system() == "Windows":
            return "cmd"
        else:
            # Try to detect the current shell
            shell = os.environ.get("SHELL", "/bin/bash")
            if "zsh" in shell:
                return "zsh"
            return "bash"
    
    def _find_shell_path(self, shell_name):
        """Find the path to a shell executable"""
        # For Windows, use the shell name directly
        if platform.system() == "Windows":
            return shell_name
            
        # Common locations for shells on Unix-like systems
        common_paths = [
            f"/bin/{shell_name}",
            f"/usr/bin/{shell_name}",
            f"/usr/local/bin/{shell_name}",
            f"{os.path.expanduser('~')}/.local/bin/{shell_name}"
        ]
        
        # Check if shell exists in common locations
        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
                
        # Try to locate shell using 'which' command
        try:
            result = subprocess.run(
                ["which", shell_name], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                path = result.stdout.strip()
                if path and os.path.exists(path):
                    return path
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
            
        return None
        
    def _spawn_shell(self):
        """Spawn a new shell process"""
        self.shell_pid = None
        
        # Windows needs special handling
        if platform.system() == "Windows":
            if self.shell_type == "cmd":
                self.shell = pexpect.spawnu('cmd.exe')
            elif self.shell_type == "powershell":
                self.shell = pexpect.spawnu('powershell.exe')
            else:
                # Fallback to cmd if specific shell not available
                self.shell = pexpect.spawnu('cmd.exe')
                self.shell_type = "cmd"
        else:
            # Unix-like systems
            shell_path = self._find_shell_path(self.shell_type)
            
            if shell_path:
                try:
                    self.shell = pexpect.spawnu(shell_path)
                except Exception as e:
                    self._append_output(f"Error spawning shell {self.shell_type}: {str(e)}", output_type="error")
                    # Fallback to system default shell
                    self.shell_type = "bash" 
                    shell_path = self._find_shell_path("bash")
                    if shell_path:
                        self.shell = pexpect.spawnu(shell_path)
                    else:
                        # Last resort fallback
                        self.shell = pexpect.spawnu('/bin/sh')
                        self.shell_type = "sh"
            else:
                # Fallback to bash if specific shell not available
                self._append_output(f"Shell {self.shell_type} not found, falling back to bash", output_type="warning")
                self.shell_type = "bash"
                shell_path = self._find_shell_path("bash")
                if shell_path:
                    self.shell = pexpect.spawnu(shell_path)
                else:
                    # Last resort fallback
                    self.shell = pexpect.spawnu('/bin/sh')
                    self.shell_type = "sh"
        
        # Store the PID for cleanup
        self.shell_pid = self.shell.pid
        
        # Get the initial prompt - wait for shell prompt pattern
        try:
            self.shell.expect([SHELL_PROMPT_PATTERN, pexpect.EOF, pexpect.TIMEOUT], timeout=2)
            self._append_output(f"Shell initialized: {self.shell_type}", output_type="info")
        except Exception as e:
            self._append_output(f"Warning: Shell initialization may be incomplete: {str(e)}", output_type="warning")
    
    def execute_command(self, command):
        """Execute a command in the shell process"""
        if not command.strip():
            return
        
        # Add command to history
        self.command_history.append(command)
        
        # Format and append the command to output
        self._append_output(f"$ {command}", output_type="command")
        
        try:
            # Send command to the shell
            self.shell.sendline(command)
            
            # Wait for command to complete
            self.shell.expect([SHELL_PROMPT_PATTERN, pexpect.EOF, pexpect.TIMEOUT], timeout=30)
            
            # Get the output and append to history
            output = self.shell.before
            if output and isinstance(output, str) and command in output:
                # Remove the command itself from the output
                output = output[output.find(command) + len(command):]
            
            # Check if the command failed by exit code
            self.shell.sendline("echo $?")
            self.shell.expect([SHELL_PROMPT_PATTERN, pexpect.EOF], timeout=5)
            exit_code_output = self.shell.before
            
            # Safe extraction of exit code
            try:
                if exit_code_output and isinstance(exit_code_output, str):
                    exit_code = int(exit_code_output.strip().split('\n')[-1])
                else:
                    exit_code = 1  # Assume error if we can't get exit code
            except (ValueError, IndexError):
                exit_code = 1  # Assume error on parsing failures
            
            output_type = "error" if exit_code != 0 else "output"
            self._append_output(output, output_type=output_type)
            
        except pexpect.TIMEOUT:
            self._append_output("Command timed out", output_type="error")
        except pexpect.EOF:
            self._append_output("Shell process ended", output_type="error")
            # Try to respawn the shell
            self._spawn_shell()
        except Exception as e:
            self._append_output(f"Error: {str(e)}", output_type="error")
    
    def change_shell(self, new_shell_type):
        """Change the current shell type"""
        if new_shell_type == self.shell_type:
            return
        
        self.cleanup()
        self.shell_type = new_shell_type
        self._spawn_shell()
        self._append_output(f"Switched to {new_shell_type}", output_type="info")
    
    def get_current_shell(self):
        """Get the current shell type"""
        return self.shell_type
    
    def _append_output(self, text, output_type="output"):
        """Append output to the history with type information"""
        if not text:
            return
            
        # Clean up the text
        if isinstance(text, str):
            lines = text.strip().split('\n')
        else:
            # Convert bytes to string if needed
            try:
                lines = text.decode('utf-8').strip().split('\n')
            except (AttributeError, UnicodeDecodeError):
                lines = str(text).strip().split('\n')
        
        # Add each line to history with type
        for line in lines:
            if line.strip():
                self.output_history.append((line, output_type))
        
        # Limit the history size
        if len(self.output_history) > 1000:
            self.output_history = self.output_history[-1000:]
    
    def get_formatted_output(self):
        """Get the terminal output as FormattedText for prompt_toolkit"""
        result = []
        
        for line, output_type in self.output_history:
            style = ""
            if output_type == "command":
                style = "bold"
            elif output_type == "error":
                style = "class:command-error"
            elif output_type == "output":
                style = "class:command-output"
            elif output_type == "info":
                style = "class:info-message"
            
            result.append((style, line + '\n'))
        
        return FormattedText(result)
    
    def clear_output(self):
        """Clear the terminal output history"""
        self.output_history = []
        self._append_output("Terminal output cleared", output_type="info")
    
    def cleanup(self):
        """Clean up resources before exit"""
        if self.shell_pid:
            try:
                self.shell.terminate(force=True)
            except:
                # Try to kill the process if termination fails
                if platform.system() == "Windows":
                    subprocess.run(f"taskkill /F /PID {self.shell_pid}", shell=True)
                else:
                    subprocess.run(f"kill -9 {self.shell_pid}", shell=True)
