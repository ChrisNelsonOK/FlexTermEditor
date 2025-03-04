"""
Snippets - Code snippet management for the editor
"""

import os
import json
import re
from typing import Dict, List, Tuple, Optional

# Define a basic structure for snippets
class Snippet:
    """Represents a code snippet with placeholder support"""
    def __init__(self, name: str, prefix: str, body: List[str], description: str = "", language: str = ""):
        """
        Initialize a snippet
        
        Args:
            name: Snippet name/identifier
            prefix: Text that triggers the snippet
            body: List of lines for the snippet content
            description: Description of the snippet
            language: Language this snippet applies to
        """
        self.name = name
        self.prefix = prefix
        self.body = body
        self.description = description
        self.language = language
        self._placeholders = self._parse_placeholders()
    
    def _parse_placeholders(self) -> List[Tuple[int, str]]:
        """
        Parse placeholders in the snippet body
        
        Returns:
            List of (position, placeholder) tuples
        """
        placeholders = []
        placeholder_pattern = r'\${(\d+)(?::([^}]*))?}'
        
        # Join all lines to find placeholders across the entire snippet
        full_text = '\n'.join(self.body)
        
        # Find all placeholders
        matches = re.finditer(placeholder_pattern, full_text)
        for match in matches:
            position = match.start()
            placeholder_text = match.group(0)
            placeholder_num = int(match.group(1))
            default_value = match.group(2) or ""
            
            # Store placeholder information as a tuple
            placeholders.append((position, placeholder_text, placeholder_num, default_value))
        
        # Sort by placeholder number
        return sorted(placeholders, key=lambda x: x[2])
    
    def get_display_text(self) -> str:
        """
        Get the display text for the snippet in completion menu
        
        Returns:
            Formatted string for display
        """
        # First line of body with placeholders simplified
        display_line = self.body[0] if self.body else ""
        
        # Replace placeholders with simpler representation
        placeholder_pattern = r'\${(\d+)(?::([^}]*))?}'
        display_line = re.sub(placeholder_pattern, lambda m: m.group(2) or f"[{m.group(1)}]", display_line)
        
        # Truncate if too long
        if len(display_line) > 50:
            display_line = display_line[:47] + "..."
            
        return display_line
    
    def get_expanded_text(self) -> str:
        """
        Get the expanded text of the snippet with default placeholder values
        
        Returns:
            The expanded snippet text
        """
        text = '\n'.join(self.body)
        
        # Replace placeholders with their default values
        placeholder_pattern = r'\${(\d+)(?::([^}]*))?}'
        text = re.sub(placeholder_pattern, lambda m: m.group(2) or "", text)
        
        return text
    
    def get_insertion_text(self) -> Tuple[str, List[Tuple[int, int, str]]]:
        """
        Get the text to insert and a list of placeholder positions
        
        Returns:
            Tuple of (text, list of placeholder positions) where positions are
            (start_pos, end_pos, placeholder_text) tuples
        """
        text = '\n'.join(self.body)
        placeholder_info = []
        
        # Replace placeholders with their default values, but record positions
        placeholder_pattern = r'\${(\d+)(?::([^}]*))?}'
        
        # First, collect all placeholder matches
        matches = list(re.finditer(placeholder_pattern, text))
        
        # Calculate character offset adjustments as we replace placeholders
        offset = 0
        for match in matches:
            original_start = match.start()
            original_text = match.group(0)
            placeholder_num = int(match.group(1))
            default_value = match.group(2) or ""
            
            # Adjust position based on previous replacements
            adjusted_start = original_start - offset
            
            # Record placeholder info (position, length, default text)
            placeholder_info.append((placeholder_num, adjusted_start, len(default_value), default_value))
            
            # Update the offset for future adjustments
            offset += len(original_text) - len(default_value)
        
        # Now replace all placeholders with their default values
        text = re.sub(placeholder_pattern, lambda m: m.group(2) or "", text)
        
        # Sort placeholder info by placeholder number
        placeholder_info.sort(key=lambda x: x[0])
        
        # Convert to (start, end, text) format for the editor
        placeholder_positions = []
        for _, start, length, default_text in placeholder_info:
            # If default text is empty, use a descriptive placeholder
            display_text = default_text if default_text else "placeholder"
            placeholder_positions.append((start, start + length, display_text))
        
        return text, placeholder_positions

class SnippetManager:
    """Manages code snippets for the editor"""
    def __init__(self, snippets_dir=None):
        """Initialize the snippet manager"""
        self.snippets_dir = snippets_dir or os.path.join(os.path.dirname(__file__), 'snippets')
        self.snippets: Dict[str, List[Snippet]] = {}
        self.load_snippets()
    
    def load_snippets(self):
        """Load snippets from the snippets directory"""
        # Create directory if it doesn't exist
        if not os.path.exists(self.snippets_dir):
            os.makedirs(self.snippets_dir)
            self._create_default_snippets()
        
        # Clear existing snippets
        self.snippets = {}
        
        # Load all JSON files in the snippets directory
        for filename in os.listdir(self.snippets_dir):
            if filename.endswith('.json'):
                language = os.path.splitext(filename)[0]
                self.snippets[language] = []
                
                try:
                    with open(os.path.join(self.snippets_dir, filename), 'r') as f:
                        snippet_data = json.load(f)
                        
                        # Process each snippet
                        for name, data in snippet_data.items():
                            if isinstance(data, dict) and 'prefix' in data and 'body' in data:
                                prefix = data['prefix']
                                body = data['body'] if isinstance(data['body'], list) else [data['body']]
                                description = data.get('description', '')
                                
                                snippet = Snippet(name, prefix, body, description, language)
                                self.snippets[language].append(snippet)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error loading snippets from {filename}: {e}")
    
    def _create_default_snippets(self):
        """Create default snippets for common languages"""
        # Python snippets
        python_snippets = {
            "For Loop": {
                "prefix": "for",
                "body": ["for ${1:item} in ${2:items}:", "    ${3:pass}"],
                "description": "For loop"
            },
            "If Statement": {
                "prefix": "if",
                "body": ["if ${1:condition}:", "    ${2:pass}"],
                "description": "If statement"
            },
            "Function": {
                "prefix": "def",
                "body": ["def ${1:function_name}(${2:parameters}):", "    \"\"\"${3:Docstring}\"\"\"", "    ${4:pass}"],
                "description": "Function definition"
            },
            "Class": {
                "prefix": "class",
                "body": ["class ${1:ClassName}:", "    \"\"\"${2:Class docstring}\"\"\"", "    def __init__(self, ${3:parameters}):", "        ${4:pass}"],
                "description": "Class definition"
            },
            "Try/Except": {
                "prefix": "try",
                "body": ["try:", "    ${1:pass}", "except ${2:Exception} as ${3:e}:", "    ${4:pass}"],
                "description": "Try/except block"
            }
        }
        
        # JavaScript snippets
        javascript_snippets = {
            "Function": {
                "prefix": "function",
                "body": ["function ${1:name}(${2:parameters}) {", "    ${3:// code}", "}"],
                "description": "Function definition"
            },
            "Arrow Function": {
                "prefix": "arrow",
                "body": ["const ${1:name} = (${2:parameters}) => {", "    ${3:// code}", "};"],
                "description": "Arrow function"
            },
            "For Loop": {
                "prefix": "for",
                "body": ["for (let ${1:i} = 0; ${1:i} < ${2:array}.length; ${1:i}++) {", "    ${3:// code}", "}"],
                "description": "For loop"
            },
            "If Statement": {
                "prefix": "if",
                "body": ["if (${1:condition}) {", "    ${2:// code}", "}"],
                "description": "If statement"
            },
            "Try/Catch": {
                "prefix": "try",
                "body": ["try {", "    ${1:// code}", "} catch (${2:error}) {", "    ${3:// error handling}", "}"],
                "description": "Try/catch block"
            }
        }
        
        # HTML snippets
        html_snippets = {
            "HTML5 Boilerplate": {
                "prefix": "html5",
                "body": [
                    "<!DOCTYPE html>",
                    "<html lang=\"en\">",
                    "<head>",
                    "    <meta charset=\"UTF-8\">",
                    "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
                    "    <title>${1:Document}</title>",
                    "</head>",
                    "<body>",
                    "    ${2:<!-- content -->}",
                    "</body>",
                    "</html>"
                ],
                "description": "HTML5 document boilerplate"
            },
            "Div": {
                "prefix": "div",
                "body": ["<div class=\"${1:class}\">${2:content}</div>"],
                "description": "Div element"
            },
            "Unordered List": {
                "prefix": "ul",
                "body": ["<ul>", "    <li>${1:item1}</li>", "    <li>${2:item2}</li>", "    <li>${3:item3}</li>", "</ul>"],
                "description": "Unordered list"
            }
        }
        
        # Write snippets to files
        os.makedirs(self.snippets_dir, exist_ok=True)
        
        with open(os.path.join(self.snippets_dir, 'python.json'), 'w') as f:
            json.dump(python_snippets, f, indent=2)
        
        with open(os.path.join(self.snippets_dir, 'javascript.json'), 'w') as f:
            json.dump(javascript_snippets, f, indent=2)
        
        with open(os.path.join(self.snippets_dir, 'html.json'), 'w') as f:
            json.dump(html_snippets, f, indent=2)
    
    def get_snippets_for_language(self, language: str) -> List[Snippet]:
        """
        Get snippets for a specific language
        
        Args:
            language: Language identifier
            
        Returns:
            List of snippets for the language
        """
        return self.snippets.get(language, [])
    
    def get_matching_snippets(self, language: str, prefix: str) -> List[Snippet]:
        """
        Get snippets that match a given prefix
        
        Args:
            language: Language identifier
            prefix: Text that might trigger snippets
            
        Returns:
            List of matching snippets
        """
        snippets = self.get_snippets_for_language(language)
        matches = []
        
        for snippet in snippets:
            if snippet.prefix.startswith(prefix):
                matches.append(snippet)
        
        return matches
    
    def get_all_languages(self) -> List[str]:
        """
        Get a list of all languages with snippets
        
        Returns:
            List of language identifiers
        """
        return list(self.snippets.keys())

# Global snippet manager instance
_snippet_manager = None

def get_snippet_manager() -> SnippetManager:
    """
    Get the global snippet manager instance
    
    Returns:
        SnippetManager instance
    """
    global _snippet_manager
    if _snippet_manager is None:
        _snippet_manager = SnippetManager()
    return _snippet_manager