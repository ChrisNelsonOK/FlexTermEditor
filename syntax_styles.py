#!/usr/bin/env python3
"""
Syntax Styles - Enhanced syntax highlighting styles for different languages
"""

import re
from pygments.token import (
    Token, Keyword, Name, Comment, String, Error, Number, Operator, 
    Generic, Whitespace, Punctuation, Other, Literal
)

# Base styles that will be applied to all languages
BASE_STYLES = {
    Token:              '#f8f8f2',  # Default style
    Whitespace:         '#f8f8f2',
    Comment:            '#888888 italic',
    Comment.Hashbang:   '#75715e',
    Comment.Multiline:  '#75715e',
    Comment.Preproc:    '#75715e',
    Comment.Single:     '#888888 italic',
    Comment.Special:    '#75715e',
    
    Keyword:            '#ff79c6',
    Keyword.Constant:   '#bd93f9',
    Keyword.Declaration: '#8be9fd italic',
    Keyword.Namespace:  '#ff79c6',
    Keyword.Pseudo:     '#ff79c6',
    Keyword.Reserved:   '#ff79c6',
    Keyword.Type:       '#8be9fd',
    
    Operator:           '#ff79c6',
    Operator.Word:      '#ff79c6',
    
    Name:               '#f8f8f2',
    Name.Attribute:     '#50fa7b',
    Name.Builtin:       '#8be9fd',
    Name.Builtin.Pseudo: '#f8f8f2',
    Name.Class:         '#8be9fd',
    Name.Constant:      '#bd93f9',
    Name.Decorator:     '#50fa7b',
    Name.Entity:        '#f8f8f2',
    Name.Exception:     '#ff5555',
    Name.Function:      '#50fa7b',
    Name.Function.Magic: '#50fa7b',
    Name.Label:         '#f8f8f2',
    Name.Namespace:     '#f8f8f2',
    Name.Other:         '#f8f8f2',
    Name.Tag:           '#ff79c6',
    Name.Variable:      '#f8f8f2',
    Name.Variable.Class: '#8be9fd',
    Name.Variable.Global: '#f8f8f2',
    Name.Variable.Instance: '#f8f8f2',
    Name.Variable.Magic: '#bd93f9',
    
    String:             '#f1fa8c',
    String.Affix:       '#f1fa8c',
    String.Backtick:    '#f1fa8c',
    String.Char:        '#f1fa8c',
    String.Delimiter:   '#f1fa8c',
    String.Doc:         '#f1fa8c',
    String.Double:      '#f1fa8c',
    String.Escape:      '#ff79c6',
    String.Heredoc:     '#f1fa8c',
    String.Interpol:    '#f1fa8c',
    String.Other:       '#f1fa8c',
    String.Regex:       '#f1fa8c',
    String.Single:      '#f1fa8c',
    String.Symbol:      '#f1fa8c',
    
    Number:             '#bd93f9',
    Number.Bin:         '#bd93f9',
    Number.Float:       '#bd93f9',
    Number.Hex:         '#bd93f9',
    Number.Integer:     '#bd93f9',
    Number.Integer.Long: '#bd93f9',
    Number.Oct:         '#bd93f9',
    
    Generic:            '#f8f8f2',
    Generic.Deleted:    '#ff5555',
    Generic.Emph:       '#f8f8f2 underline',
    Generic.Error:      '#ff5555',
    Generic.Heading:    '#f8f8f2 bold',
    Generic.Inserted:   '#50fa7b',
    Generic.Output:     '#44475a',
    Generic.Prompt:     '#f8f8f2',
    Generic.Strong:     '#f8f8f2',
    Generic.Subheading: '#f8f8f2 bold',
    Generic.Traceback:  '#ff5555',
    
    Error:              '#ff5555',
    Punctuation:        '#f8f8f2',
}

# Language-specific syntax highlighting styles
LANGUAGE_STYLES = {
    # Python-specific highlights
    'python': {
        Keyword:            '#ff79c6 bold',
        Name.Builtin:       '#8be9fd bold',          # Built-in functions
        Name.Builtin.Pseudo: '#8be9fd italic',       # self, cls, etc.
        Name.Function:      '#50fa7b bold',          # Function definitions
        Name.Class:         '#8be9fd bold',          # Class definitions
        Name.Decorator:     '#50fa7b italic',        # Decorators
        String.Doc:         '#6272a4 italic',        # Docstrings
        Comment:            '#6272a4 italic',        # Comments
        # Special Python operators
        Operator.Word:      '#ff79c6 bold',          # and, or, not, in, is
        # f-string highlighting
        String.Interpol:    '#ffb86c',               # Interpolation parts
    },
    
    # JavaScript-specific highlights
    'javascript': {
        Keyword:            '#ff79c6 bold',
        Keyword.Constant:   '#bd93f9 bold',          # true, false, null, undefined
        Name.Function:      '#50fa7b bold',
        Name.Function.Magic: '#50fa7b italic',       # Arrow functions
        String.Interpol:    '#ffb86c',               # Template literals
        Name.Other:         '#f8f8f2',
        Operator:           '#ff79c6',
        Name.Builtin:       '#8be9fd bold',          # console, document, etc.
        Name.Class:         '#8be9fd bold',          # Class definitions
        Comment:            '#6272a4 italic',
    },
    
    # HTML-specific highlights
    'html': {
        Name.Tag:           '#ff79c6 bold',          # HTML tags
        Name.Attribute:     '#50fa7b',               # HTML attributes
        String:             '#f1fa8c',               # Attribute values
        Comment:            '#6272a4 italic',
        Punctuation:        '#f8f8f2',
        Name.Entity:        '#bd93f9',               # HTML entities
    },
    
    # CSS-specific highlights
    'css': {
        Name.Tag:           '#ff79c6',               # Selectors
        Name.Class:         '#50fa7b',               # Class selectors
        Name.Attribute:     '#50fa7b',               # Attribute selectors
        Name.Builtin:       '#8be9fd',               # Pseudo-classes
        Name.Function:      '#ffb86c',               # Functions
        String:             '#f1fa8c',               # Values
        Number:             '#bd93f9',               # Numeric values
        Keyword:            '#ff79c6 bold',          # !important, etc.
        Comment:            '#6272a4 italic',
        Punctuation:        '#f8f8f2',
    },
    
    # Bash/Shell-specific highlights
    'shell': {
        String.Double:      '#f1fa8c',
        String.Single:      '#f1fa8c',
        Keyword:            '#ff79c6 bold',
        Keyword.Reserved:   '#ff79c6 bold',
        Name.Builtin:       '#8be9fd bold',
        Name.Variable:      '#ffb86c',               # Variable references
        Operator:           '#ff79c6',
        Comment:            '#6272a4 italic',
        Punctuation:        '#f8f8f2',
    },
    
    # SQL-specific highlights
    'sql': {
        Keyword:            '#ff79c6 bold',          # SQL keywords (SELECT, WHERE, etc.)
        Name.Builtin:       '#8be9fd bold',          # Functions
        String:             '#f1fa8c',  
        Number:             '#bd93f9',
        Comment:            '#6272a4 italic',
        Operator:           '#ff79c6',
    },
    
    # Markdown-specific highlights
    'markdown': {
        Generic.Heading:    '#ff79c6 bold',
        Generic.Subheading: '#ff79c6 bold',
        Generic.Strong:     '#ffb86c bold',
        Generic.Emph:       '#f8f8f2 italic',
        String:             '#f1fa8c',
        Keyword:            '#ff79c6',
        Name.Tag:           '#bd93f9',
        Comment:            '#6272a4 italic',
    },
    
    # JSON-specific highlights
    'json': {
        Name.Tag:           '#ff79c6',               # Keys
        String:             '#f1fa8c',               # String values
        Number:             '#bd93f9',               # Numeric values
        Keyword.Constant:   '#bd93f9 bold',          # true, false, null
        Punctuation:        '#f8f8f2',
    },
    
    # XML-specific highlights
    'xml': {
        Name.Tag:           '#ff79c6 bold',          # XML tags
        Name.Attribute:     '#50fa7b',               # XML attributes
        String:             '#f1fa8c',               # Attribute values
        Comment:            '#6272a4 italic',
        Punctuation:        '#f8f8f2',
    },
    
    # YAML-specific highlights
    'yaml': {
        Name.Tag:           '#ff79c6',               # Keys
        String:             '#f1fa8c',               # String values
        Number:             '#bd93f9',               # Numeric values
        Keyword.Constant:   '#bd93f9 bold',          # true, false, null
        Comment:            '#6272a4 italic',
        Punctuation:        '#f8f8f2',
    },
    
    # C/C++-specific highlights
    'c': {
        Keyword:            '#ff79c6 bold',
        Keyword.Type:       '#8be9fd bold',
        Name.Function:      '#50fa7b bold',
        Name.Class:         '#8be9fd bold',
        Comment:            '#6272a4 italic',
        String:             '#f1fa8c',
        Operator:           '#ff79c6',
        Punctuation:        '#f8f8f2',
    },
    
    # C/C++-specific highlights
    'cpp': {
        Keyword:            '#ff79c6 bold',
        Keyword.Type:       '#8be9fd bold',
        Name.Function:      '#50fa7b bold',
        Name.Class:         '#8be9fd bold',
        Name.Namespace:     '#bd93f9',
        Comment:            '#6272a4 italic',
        String:             '#f1fa8c',
        Operator:           '#ff79c6',
        Punctuation:        '#f8f8f2',
    },
    
    # Java-specific highlights
    'java': {
        Keyword:            '#ff79c6 bold',
        Keyword.Type:       '#8be9fd bold',
        Name.Function:      '#50fa7b bold',
        Name.Class:         '#8be9fd bold',
        Name.Namespace:     '#bd93f9',
        Comment:            '#6272a4 italic',
        String:             '#f1fa8c',
        Operator:           '#ff79c6',
        Punctuation:        '#f8f8f2',
    },
    
    # C#-specific highlights
    'csharp': {
        Keyword:            '#ff79c6 bold',
        Keyword.Type:       '#8be9fd bold',
        Name.Function:      '#50fa7b bold',
        Name.Class:         '#8be9fd bold',
        Name.Namespace:     '#bd93f9',
        Comment:            '#6272a4 italic',
        String:             '#f1fa8c',
        Operator:           '#ff79c6',
        Punctuation:        '#f8f8f2',
    },
    
    # Ruby-specific highlights
    'ruby': {
        Keyword:            '#ff79c6 bold',
        Name.Builtin:       '#8be9fd bold',
        Name.Function:      '#50fa7b bold',
        Name.Class:         '#8be9fd bold',
        Comment:            '#6272a4 italic',
        String:             '#f1fa8c',
        String.Symbol:      '#bd93f9',
        Operator:           '#ff79c6',
        Punctuation:        '#f8f8f2',
    },
    
    # Go-specific highlights
    'go': {
        Keyword:            '#ff79c6 bold',
        Keyword.Type:       '#8be9fd bold',
        Name.Function:      '#50fa7b bold',
        Name.Class:         '#8be9fd bold',
        Comment:            '#6272a4 italic',
        String:             '#f1fa8c',
        Operator:           '#ff79c6',
        Punctuation:        '#f8f8f2',
    },
    
    # Rust-specific highlights
    'rust': {
        Keyword:            '#ff79c6 bold',
        Keyword.Type:       '#8be9fd bold',
        Name.Function:      '#50fa7b bold',
        Name.Class:         '#8be9fd bold',
        Name.Decorator:     '#50fa7b italic',
        Comment:            '#6272a4 italic',
        String:             '#f1fa8c',
        Operator:           '#ff79c6',
        Punctuation:        '#f8f8f2',
    },
}

def get_syntax_styles(language, theme='dracula'):
    """
    Get syntax highlighting styles for a specific language and theme
    
    Args:
        language (str): Programming language identifier (e.g., 'python', 'javascript')
        theme (str): Theme name to use as a base (default: 'dracula')
        
    Returns:
        dict: Token-to-style mapping for syntax highlighting
    """
    # Start with the base styles
    styles = BASE_STYLES.copy()
    
    # Apply language-specific overrides if available
    language = language.lower()
    if language in LANGUAGE_STYLES:
        for token, style in LANGUAGE_STYLES[language].items():
            styles[token] = style
    
    # TODO: In the future, apply theme-specific overrides
    # This would allow specific themes to customize syntax highlighting
    
    return styles

def apply_theme_to_syntax_styles(styles, theme_name):
    """
    Adjust syntax highlighting styles based on the current theme
    
    Args:
        styles (dict): Current syntax styles
        theme_name (str): Name of the current theme
        
    Returns:
        dict: Updated syntax styles for the theme
    """
    # This is a placeholder for future theme-specific syntax adjustments
    # Could modify colors to better match each theme's palette
    return styles

def get_language_from_filename(filename):
    """
    Determine language identifier from filename
    
    Args:
        filename (str): The file name/path
        
    Returns:
        str: Language identifier or 'text' if not recognized
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