#!/usr/bin/env python3
"""
Syntax Checker - Provides on-the-fly syntax checking for code in the editor
"""

import ast
import re
import logging
import importlib
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
import threading
import time
import pycodestyle
from pygments.util import ClassNotFound
from pygments.lexers import get_lexer_for_filename

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("syntax_checker")

# Singleton instances
_syntax_check_queue = Queue()
_syntax_check_results = {}
_syntax_check_lock = threading.Lock()
_executor = ThreadPoolExecutor(max_workers=1)

# Store the most recent syntax check time for each file
_last_check_time = {}

# Constants for memory management
MAX_RESULTS_CACHE_SIZE = 50  # Maximum number of files to store results for
CACHE_CLEANUP_INTERVAL = 300  # Cleanup interval in seconds (5 minutes)
_last_cache_cleanup_time = time.time()

class SyntaxError:
    """Represents a syntax or style error in the code"""
    def __init__(self, line_number, column, message, error_type="syntax"):
        self.line_number = line_number
        self.column = column
        self.message = message
        self.error_type = error_type  # "syntax" or "style"
    
    def __str__(self):
        return f"Line {self.line_number}, Col {self.column}: {self.message} ({self.error_type})"

def get_language_from_filename(filename):
    """Determine the language based on file extension"""
    if not filename:
        return "text"
    
    try:
        lexer = get_lexer_for_filename(filename)
        return lexer.name.lower()
    except ClassNotFound:
        return "text"

def check_python_syntax(code):
    """Check Python code for syntax errors"""
    errors = []
    
    # Check for syntax errors
    try:
        ast.parse(code)
    except Exception as e:
        # Handle Python's SyntaxError
        if hasattr(e, 'lineno') and hasattr(e, 'offset'):
            line_number = getattr(e, 'lineno', 1)
            column = getattr(e, 'offset', 0) or 0
            message = str(e)
            # Remove the file name and line/column info from the message
            if ": " in message:
                message = message.split(": ", 1)[1]
            errors.append(SyntaxError(line_number, column, message, "syntax"))
        else:
            # Fallback for other kinds of syntax errors
            errors.append(SyntaxError(1, 0, str(e), "syntax"))
    
    return errors

def check_python_style(code):
    """Check Python code for style issues (PEP 8)"""
    errors = []
    
    style_checker = pycodestyle.StyleGuide(quiet=True)
    
    # Use a temporary file object to check the code
    file_lines = code.splitlines(True)
    file_errors = style_checker.check_lines(file_lines)
    
    for line_number, offset, message, _ in file_errors:
        # Filter out specific style errors if needed
        errors.append(SyntaxError(line_number, offset, message, "style"))
    
    return errors

def check_javascript_syntax(code):
    """Check JavaScript code for basic syntax errors"""
    errors = []
    
    # Very basic JavaScript syntax checks
    # Check for unmatched brackets/parentheses
    stack = []
    brackets = {')': '(', '}': '{', ']': '['}
    
    lines = code.split('\n')
    for line_num, line in enumerate(lines, 1):
        for col, char in enumerate(line, 1):
            if char in '({[':
                stack.append((char, line_num, col))
            elif char in ')}]':
                if not stack or stack[-1][0] != brackets[char]:
                    errors.append(SyntaxError(line_num, col, f"Unmatched {char}", "syntax"))
                else:
                    stack.pop()
    
    # Report any unclosed brackets
    for char, line_num, col in stack:
        errors.append(SyntaxError(line_num, col, f"Unclosed {char}", "syntax"))
    
    return errors

def check_syntax(code, filename=None):
    """Check code syntax based on file type"""
    if not code.strip():
        return []  # Skip empty code
    
    language = get_language_from_filename(filename)
    
    try:
        if "python" in language:
            return check_python_syntax(code) + check_python_style(code)
        elif "javascript" in language or "js" in language:
            return check_javascript_syntax(code)
        else:
            # For other languages, do basic bracket checking
            return check_javascript_syntax(code)  # Reuse the bracket check
    except Exception as e:
        logger.error(f"Error during syntax checking: {e}")
        return []

def request_syntax_check(text, filename=None):
    """Request a syntax check for the given text and filename
    
    Args:
        text (str): The code text to check
        filename (str, optional): The filename to determine language
        
    Returns:
        None: Check is performed asynchronously
    """
    # Add to queue - will replace any previous request for the same file
    _syntax_check_queue.put((text, filename))
    
    # Throttle to avoid too frequent checking for the same file
    current_time = time.time()
    if filename in _last_check_time and current_time - _last_check_time[filename] < 2.0:
        return  # Skip if checked within last 2 seconds
    
    _last_check_time[filename] = current_time
    
    # Ensure the background thread is running
    ensure_checker_running()

def ensure_checker_running():
    """Ensure the background syntax checker is running"""
    # Check if we already submitted the task
    global _executor
    
    # Submit the task if it's not already running
    _executor.submit(process_syntax_check_queue)

def cleanup_syntax_cache():
    """Clean up the syntax check cache to prevent memory leaks"""
    global _last_cache_cleanup_time
    
    # Only run cleanup periodically
    current_time = time.time()
    if current_time - _last_cache_cleanup_time < CACHE_CLEANUP_INTERVAL:
        return
    
    logger.debug("Performing syntax check cache cleanup")
    
    with _syntax_check_lock:
        # If cache is smaller than the limit, no need to clean up
        if len(_syntax_check_results) <= MAX_RESULTS_CACHE_SIZE:
            _last_cache_cleanup_time = current_time
            return
            
        # Sort files by last check time (most recent first)
        sorted_files = sorted(
            [(f, _last_check_time.get(f, 0)) for f in _syntax_check_results],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Keep only the most recently used files
        files_to_keep = sorted_files[:MAX_RESULTS_CACHE_SIZE]
        files_to_remove = sorted_files[MAX_RESULTS_CACHE_SIZE:]
        
        # Remove old entries from results and last check time
        for filename, _ in files_to_remove:
            if filename in _syntax_check_results:
                del _syntax_check_results[filename]
            if filename in _last_check_time:
                del _last_check_time[filename]
        
        logger.debug(f"Cleaned up {len(files_to_remove)} entries from syntax check cache")
        _last_cache_cleanup_time = current_time

def process_syntax_check_queue():
    """Process the syntax check queue in a background thread"""
    while True:
        try:
            # Get the latest item from the queue (waiting up to 5 seconds)
            text, filename = _syntax_check_queue.get(timeout=5)
            
            # Perform the syntax check
            errors = check_syntax(text, filename)
            
            # Store the results
            with _syntax_check_lock:
                _syntax_check_results[filename] = errors
            
            # Periodically clean up the cache to prevent memory leaks
            cleanup_syntax_cache()
            
            # Mark the task as done
            _syntax_check_queue.task_done()
            
        except Empty:
            # If the queue is empty for 5 seconds, exit the thread
            return
        except Exception as e:
            logger.error(f"Error processing syntax check: {e}")
            
            # Mark the task as done even if there was an error
            _syntax_check_queue.task_done()

def get_syntax_errors(filename):
    """Get the syntax errors for the given filename
    
    Args:
        filename (str): The filename to get errors for
        
    Returns:
        list: List of SyntaxError objects, or empty list if none
    """
    with _syntax_check_lock:
        return _syntax_check_results.get(filename, [])

def shutdown_checker():
    """Shutdown the syntax checker (call when exiting the application)"""
    global _executor
    _executor.shutdown(wait=False)