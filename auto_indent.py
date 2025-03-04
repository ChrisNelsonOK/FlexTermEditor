#!/usr/bin/env python3
"""
Auto-Indentation - Handles smart code indentation for various languages
"""

import re

def get_indent_size(text, use_tabs=False):
    """
    Get the indentation size from text.
    Returns tab character if use_tabs is True, otherwise returns spaces.
    """
    if use_tabs:
        return '\t'
    
    # Find all leading whitespace in the document
    leading_spaces = re.findall(r'^\s+', text, re.MULTILINE)
    
    if not leading_spaces:
        return '    '  # Default to 4 spaces if no indentation detected
    
    # Count spaces in each leading whitespace
    space_counts = [len(spaces.replace('\t', '    ')) for spaces in leading_spaces]
    
    # Filter out zero counts
    non_zero_counts = [count for count in space_counts if count > 0]
    
    if not non_zero_counts:
        return '    '  # Default to 4 spaces
    
    # Find the most common indent by GCD
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    
    if len(non_zero_counts) == 1:
        indent_size = non_zero_counts[0]
    else:
        indent_size = non_zero_counts[0]
        for count in non_zero_counts[1:]:
            indent_size = gcd(indent_size, count)
    
    # If the indent size is 0 or unreasonably large, default to 4
    if indent_size == 0 or indent_size > 8:
        indent_size = 4
    
    return ' ' * indent_size

def should_increase_indent(line, language="python"):
    """
    Determine if the next line should have increased indentation.
    """
    if language == "python":
        # Check for Python block starters
        if re.search(r':\s*(#.*)?$', line):  # Lines ending with : (ignoring comments)
            return True
        
    elif language in ["javascript", "typescript", "java", "c", "cpp", "csharp"]:
        # Check for C-style block starters
        if '{' in line and '}' not in line:
            return True
        # Handle special cases like if/for/while statements without braces
        if re.search(r'(if|for|while|else)\s*\(.*\)\s*(//.*)?$', line):
            return True
    
    elif language in ["html", "xml"]:
        # Check for opening tags without closing tags
        opening_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*>', line)
        closing_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9]*)>', line)
        self_closing = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*/>', line)
        
        # Count tags that are opened but not closed
        open_count = len(opening_tags) - len(closing_tags) - len(self_closing)
        return open_count > 0
        
    return False

def should_decrease_indent(line, language="python"):
    """
    Determine if the current line should have decreased indentation.
    """
    if language == "python":
        # Check for Python dedent patterns
        if re.match(r'\s*(else|elif|except|finally):', line):
            return True
            
    elif language in ["javascript", "typescript", "java", "c", "cpp", "csharp"]:
        # Check for C-style block enders
        if '}' in line and '{' not in line:
            return True
        # Check for else without braces
        if re.match(r'\s*else\s*(//.*)?$', line):
            return True
            
    elif language in ["html", "xml"]:
        # Check if line starts with a closing tag
        if re.match(r'\s*</[a-zA-Z][a-zA-Z0-9]*>', line):
            return True
    
    return False

def get_smart_indent(text, cursor_position, language="python"):
    """
    Determine the appropriate indentation for the next line.
    
    Args:
        text: The entire document text
        cursor_position: The current cursor position
        language: The programming language for language-specific rules
    
    Returns:
        The indentation string to use for the next line
    """
    # Get the indentation size
    indent_str = get_indent_size(text)
    
    # Get the current line
    lines = text[:cursor_position].split('\n')
    if not lines:
        return ''
    
    current_line = lines[-1]
    # Match leading whitespace, safely handling empty lines
    indent_match = re.match(r'^\s*', current_line)
    current_indent = indent_match.group(0) if indent_match else ''
    
    # Check if we need to increase indentation
    if should_increase_indent(current_line, language):
        return current_indent + indent_str
    
    # If the current line should decrease indentation, but we're already at the cursor,
    # we don't want to modify the current line's indentation
    
    # For a new line, just keep the same indentation as the current line
    return current_indent

def get_language_from_filename(filename):
    """
    Determine the language based on file extension.
    """
    if not filename:
        return "text"
        
    extension = filename.split('.')[-1].lower() if '.' in filename else ''
    
    language_map = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'html': 'html',
        'xml': 'xml',
        'java': 'java',
        'c': 'c',
        'cpp': 'cpp',
        'cc': 'cpp',
        'h': 'c',
        'hpp': 'cpp',
        'cs': 'csharp',
        'php': 'php',
        'rb': 'ruby',
        'pl': 'perl',
        'sh': 'shell',
        'bash': 'shell',
        'zsh': 'shell',
        'json': 'json',
        'md': 'markdown',
        'css': 'css',
        'scss': 'scss',
        'less': 'less',
        'sql': 'sql',
        'yaml': 'yaml',
        'yml': 'yaml',
        'go': 'go',
        'rs': 'rust',
    }
    
    return language_map.get(extension, 'text')

def apply_auto_indent(buffer, event):
    """
    Apply auto-indentation when Enter is pressed.
    
    Args:
        buffer: The current buffer
        event: The key event
    
    Returns:
        True if the indentation was handled, False otherwise
    """
    # Get the document text and cursor position
    text = buffer.text
    cursor_position = buffer.cursor_position
    
    # Determine the language for the current file
    filename = getattr(buffer, 'filename', None)
    language = get_language_from_filename(filename) if filename else 'text'
    
    # Get the appropriate indentation
    indent = get_smart_indent(text, cursor_position, language)
    
    # Insert a new line with proper indentation
    buffer.insert_text('\n' + indent)
    
    return True  # Return True to indicate we've handled the key press