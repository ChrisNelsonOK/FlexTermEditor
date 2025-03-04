"""
AI Snippets - AI-powered code snippet generation and management
"""
import os
import re
import json
import time
import threading
import logging
from typing import Dict, List, Tuple, Optional, Any, Union, Set

from snippets import Snippet, get_snippet_manager

# Set up logging
logger = logging.getLogger(__name__)

class AISnippetGenerator:
    """Generates and manages AI-powered code snippets"""
    
    def __init__(self, snippets_dir: Optional[str] = None):
        """Initialize the AI snippet generator
        
        Args:
            snippets_dir: Optional directory for storing AI-generated snippets
        """
        self.snippet_manager = get_snippet_manager()
        self.snippets_dir = snippets_dir or os.path.join(os.path.dirname(__file__), 'ai_snippets')
        
        # Create AI snippets directory if it doesn't exist
        if not os.path.exists(self.snippets_dir):
            os.makedirs(self.snippets_dir)
        
        # Dictionary to store AI-generated snippets
        self.ai_snippets: Dict[str, List[Snippet]] = {}
        
        # Load existing AI snippets
        self._load_ai_snippets()
        
        # Cache of recently generated snippets to avoid duplicates
        self.recent_generations: Dict[str, Dict[str, Any]] = {}
        
        # Lock for thread safety when adding snippets
        self.snippet_lock = threading.Lock()
    
    def _load_ai_snippets(self) -> None:
        """Load AI-generated snippets from disk"""
        try:
            # Clear existing snippets
            self.ai_snippets = {}
            
            # Load all JSON files in the snippets directory
            if os.path.exists(self.snippets_dir):
                for filename in os.listdir(self.snippets_dir):
                    if filename.endswith('.json'):
                        language = os.path.splitext(filename)[0]
                        self.ai_snippets[language] = []
                        
                        try:
                            with open(os.path.join(self.snippets_dir, filename), 'r') as f:
                                snippet_data = json.load(f)
                                
                                # Process each snippet
                                for name, data in snippet_data.items():
                                    if isinstance(data, dict) and 'prefix' in data and 'body' in data:
                                        prefix = data['prefix']
                                        body = data['body'] if isinstance(data['body'], list) else [data['body']]
                                        description = data.get('description', 'AI-generated snippet')
                                        
                                        snippet = Snippet(name, prefix, body, description, language)
                                        self.ai_snippets[language].append(snippet)
                        except (json.JSONDecodeError, IOError) as e:
                            logger.error(f"Error loading AI snippets from {filename}: {e}")
        except Exception as e:
            logger.error(f"Error loading AI snippets: {e}")
    
    def _save_ai_snippets(self, language: str) -> None:
        """Save AI-generated snippets to disk for a specific language
        
        Args:
            language: Language identifier
        """
        try:
            # Skip if no snippets for this language
            if language not in self.ai_snippets or not self.ai_snippets[language]:
                return
                
            # Create snippets dictionary
            snippets_dict = {}
            for snippet in self.ai_snippets[language]:
                snippets_dict[snippet.name] = {
                    'prefix': snippet.prefix,
                    'body': snippet.body,
                    'description': snippet.description
                }
            
            # Save to file
            file_path = os.path.join(self.snippets_dir, f"{language}.json")
            with open(file_path, 'w') as f:
                json.dump(snippets_dict, f, indent=2)
                
            logger.debug(f"Saved {len(snippets_dict)} AI snippets for {language}")
        except Exception as e:
            logger.error(f"Error saving AI snippets for {language}: {e}")
    
    def generate_snippet_from_description(self, 
                                        language: str, 
                                        name: str, 
                                        description: str, 
                                        prefix: Optional[str] = None) -> Optional[Snippet]:
        """Generate a code snippet based on a description
        
        Args:
            language: Programming language (e.g., 'python', 'javascript')
            name: Name for the snippet
            description: Description of what the snippet should do
            prefix: Optional trigger text for the snippet
            
        Returns:
            Generated Snippet object or None if generation failed
        """
        # Check if we've recently generated a similar snippet
        cache_key = f"{language}:{description.lower()}"
        if cache_key in self.recent_generations:
            logger.debug(f"Using cached snippet for: {description}")
            cached = self.recent_generations[cache_key]
            return Snippet(
                name, 
                cached.get('prefix', prefix or name.lower().replace(' ', '_')),
                cached['body'],
                description,
                language
            )
        
        # Generate snippet based on language and description
        try:
            # Generate code snippet using rule-based templates with NLP-inspired
            # pattern matching for now - this can be replaced with an actual
            # AI code generation API in production
            snippet_body = self._generate_snippet_body(language, description)
            
            if not snippet_body:
                logger.warning(f"Failed to generate snippet for: {description}")
                return None
            
            # Create default prefix if none provided
            if not prefix:
                # Generate a prefix from the name (lowercase, replace spaces with underscores)
                prefix = name.lower().replace(' ', '_')
                
                # Ensure prefix is valid (no special characters except underscores)
                prefix = re.sub(r'[^\w]', '', prefix)
                
                # Make sure it's not empty
                if not prefix:
                    prefix = "ai_snippet"
            
            # Create the snippet object
            snippet = Snippet(name, prefix, snippet_body, description, language)
            
            # Cache the generation
            self.recent_generations[cache_key] = {
                'prefix': prefix,
                'body': snippet_body,
                'timestamp': time.time()
            }
            
            # Limit cache size (keep only the 50 most recent generations)
            if len(self.recent_generations) > 50:
                oldest_key = min(self.recent_generations.keys(), 
                                key=lambda k: self.recent_generations[k]['timestamp'])
                del self.recent_generations[oldest_key]
            
            return snippet
        except Exception as e:
            logger.error(f"Error generating snippet: {e}")
            return None
    
    def _generate_snippet_body(self, language: str, description: str) -> List[str]:
        """Generate code for a snippet body based on language and description
        
        Args:
            language: Programming language
            description: Description of what the snippet should do
            
        Returns:
            List of code lines for the snippet
        """
        # This implementation uses a rule-based language pattern matching system
        # with static templates. It can be replaced with an actual AI model API
        # call in production
        
        description_lower = description.lower()
        
        # Python snippets
        if language == 'python':
            if 'function' in description_lower or 'def' in description_lower:
                return [
                    "def ${1:function_name}(${2:parameters}):",
                    "    \"\"\"${3:" + description + "}\"\"\"",
                    "    ${4:# Function implementation}",
                    "    ${5:pass}"
                ]
            elif 'class' in description_lower:
                return [
                    "class ${1:ClassName}:",
                    "    \"\"\"${2:" + description + "}\"\"\"",
                    "    def __init__(self, ${3:parameters}):",
                    "        ${4:# Initialize attributes}",
                    "        ${5:pass}",
                    "    ",
                    "    def ${6:method_name}(self, ${7:parameters}):",
                    "        ${8:# Method implementation}",
                    "        ${9:pass}"
                ]
            elif 'loop' in description_lower or 'for' in description_lower:
                if 'range' in description_lower:
                    return [
                        "for ${1:i} in range(${2:n}):",
                        "    ${3:# Loop body}",
                        "    ${4:pass}"
                    ]
                else:
                    return [
                        "for ${1:item} in ${2:iterable}:",
                        "    ${3:# Loop body}",
                        "    ${4:pass}"
                    ]
            elif 'if' in description_lower or 'condition' in description_lower:
                return [
                    "if ${1:condition}:",
                    "    ${2:# If block}",
                    "    ${3:pass}",
                    "elif ${4:other_condition}:",
                    "    ${5:# Elif block}",
                    "    ${6:pass}",
                    "else:",
                    "    ${7:# Else block}",
                    "    ${8:pass}"
                ]
            elif 'try' in description_lower or 'except' in description_lower or 'error' in description_lower:
                return [
                    "try:",
                    "    ${1:# Code that might raise an exception}",
                    "    ${2:pass}",
                    "except ${3:Exception} as ${4:e}:",
                    "    ${5:# Handle the exception}",
                    "    ${6:pass}",
                    "finally:",
                    "    ${7:# Cleanup code (always executed)}",
                    "    ${8:pass}"
                ]
            elif 'import' in description_lower:
                return [
                    "import ${1:module}",
                    "from ${2:package} import ${3:submodule}",
                    "",
                    "${4:# Use the imported modules}",
                    "${5:pass}"
                ]
            elif 'file' in description_lower or 'open' in description_lower or 'read' in description_lower:
                return [
                    "with open(${1:file_path}, ${2:'r'}) as ${3:f}:",
                    "    ${4:content} = ${3:f}.read()",
                    "    ${5:# Process the file content}",
                    "    ${6:pass}"
                ]
            # Default Python snippet
            return [
                "# ${1:" + description + "}",
                "${2:# Your code here}",
                "${3:pass}"
            ]
            
        # JavaScript snippets
        elif language == 'javascript' or language == 'js':
            if 'function' in description_lower:
                if 'arrow' in description_lower:
                    return [
                        "const ${1:functionName} = (${2:parameters}) => {",
                        "  ${3:// Function implementation}",
                        "  ${4:return ${5:result};}",
                        "};"
                    ]
                else:
                    return [
                        "function ${1:functionName}(${2:parameters}) {",
                        "  ${3:// Function implementation}",
                        "  ${4:return ${5:result};}",
                        "}"
                    ]
            elif 'class' in description_lower:
                return [
                    "class ${1:ClassName} {",
                    "  constructor(${2:parameters}) {",
                    "    ${3:// Initialize properties}",
                    "    ${4:this.property = value;}",
                    "  }",
                    "  ",
                    "  ${5:methodName}(${6:parameters}) {",
                    "    ${7:// Method implementation}",
                    "    ${8:return ${9:result};}",
                    "  }",
                    "}"
                ]
            elif 'loop' in description_lower or 'for' in description_lower:
                if 'each' in description_lower:
                    return [
                        "${1:array}.forEach((${2:item}, ${3:index}) => {",
                        "  ${4:// Loop body}",
                        "});"
                    ]
                else:
                    return [
                        "for (let ${1:i} = 0; ${1:i} < ${2:array}.length; ${1:i}++) {",
                        "  ${3:const} ${4:item} = ${2:array}[${1:i}];",
                        "  ${5:// Loop body}",
                        "}"
                    ]
            elif 'if' in description_lower or 'condition' in description_lower:
                return [
                    "if (${1:condition}) {",
                    "  ${2:// If block}",
                    "} else if (${3:otherCondition}) {",
                    "  ${4:// Else if block}",
                    "} else {",
                    "  ${5:// Else block}",
                    "}"
                ]
            elif 'try' in description_lower or 'catch' in description_lower or 'error' in description_lower:
                return [
                    "try {",
                    "  ${1:// Code that might throw an error}",
                    "} catch (${2:error}) {",
                    "  ${3:// Handle the error}",
                    "} finally {",
                    "  ${4:// Cleanup code (always executed)}",
                    "}"
                ]
            elif 'import' in description_lower:
                return [
                    "import ${1:{ moduleName }} from '${2:module}';",
                    "",
                    "${3:// Use the imported module}",
                    "${4:// Your code here}"
                ]
            elif 'file' in description_lower or 'read' in description_lower:
                return [
                    "const fs = require('fs');",
                    "",
                    "fs.readFile('${1:file_path}', '${2:utf8}', (${3:err}, ${4:data}) => {",
                    "  if (${3:err}) {",
                    "    console.error(${3:err});",
                    "    return;",
                    "  }",
                    "  ${5:// Process the file content}",
                    "});"
                ]
            # Default JavaScript snippet
            return [
                "// ${1:" + description + "}",
                "${2:// Your code here}"
            ]
            
        # HTML snippets
        elif language == 'html':
            if 'form' in description_lower:
                return [
                    "<form action=\"${1:#}\" method=\"${2:post}\">",
                    "  <div class=\"${3:form-group}\">",
                    "    <label for=\"${4:input-id}\">${5:Label}</label>",
                    "    <input type=\"${6:text}\" id=\"${4:input-id}\" name=\"${7:input-name}\" class=\"${8:form-control}\">",
                    "  </div>",
                    "  <button type=\"submit\" class=\"${9:btn}\">${10:Submit}</button>",
                    "</form>"
                ]
            elif 'table' in description_lower:
                return [
                    "<table class=\"${1:table}\">",
                    "  <thead>",
                    "    <tr>",
                    "      <th>${2:Column 1}</th>",
                    "      <th>${3:Column 2}</th>",
                    "      <th>${4:Column 3}</th>",
                    "    </tr>",
                    "  </thead>",
                    "  <tbody>",
                    "    <tr>",
                    "      <td>${5:Data 1}</td>",
                    "      <td>${6:Data 2}</td>",
                    "      <td>${7:Data 3}</td>",
                    "    </tr>",
                    "  </tbody>",
                    "</table>"
                ]
            elif 'list' in description_lower:
                if 'unordered' in description_lower:
                    return [
                        "<ul class=\"${1:list}\">",
                        "  <li>${2:Item 1}</li>",
                        "  <li>${3:Item 2}</li>",
                        "  <li>${4:Item 3}</li>",
                        "</ul>"
                    ]
                else:
                    return [
                        "<ol class=\"${1:list}\">",
                        "  <li>${2:Item 1}</li>",
                        "  <li>${3:Item 2}</li>",
                        "  <li>${4:Item 3}</li>",
                        "</ol>"
                    ]
            elif 'div' in description_lower or 'container' in description_lower:
                return [
                    "<div class=\"${1:container}\">",
                    "  <div class=\"${2:row}\">",
                    "    <div class=\"${3:col}\">",
                    "      ${4:<!-- Content here -->}",
                    "    </div>",
                    "  </div>",
                    "</div>"
                ]
            elif 'nav' in description_lower or 'menu' in description_lower:
                return [
                    "<nav class=\"${1:navbar}\">",
                    "  <ul class=\"${2:nav-list}\">",
                    "    <li class=\"${3:nav-item}\"><a href=\"${4:#}\">${5:Home}</a></li>",
                    "    <li class=\"${3:nav-item}\"><a href=\"${6:#}\">${7:About}</a></li>",
                    "    <li class=\"${3:nav-item}\"><a href=\"${8:#}\">${9:Contact}</a></li>",
                    "  </ul>",
                    "</nav>"
                ]
            # Default HTML snippet
            return [
                "<!-- ${1:" + description + "} -->",
                "<div class=\"${2:container}\">",
                "  ${3:<!-- Your content here -->}",
                "</div>"
            ]
            
        # CSS snippets
        elif language == 'css':
            if 'flex' in description_lower:
                return [
                    ".${1:container} {",
                    "  display: flex;",
                    "  flex-direction: ${2:row};",
                    "  justify-content: ${3:space-between};",
                    "  align-items: ${4:center};",
                    "  ${5:/* Additional flex properties */}",
                    "}"
                ]
            elif 'grid' in description_lower:
                return [
                    ".${1:container} {",
                    "  display: grid;",
                    "  grid-template-columns: ${2:repeat(3, 1fr)};",
                    "  grid-gap: ${3:10px};",
                    "  ${4:/* Additional grid properties */}",
                    "}"
                ]
            elif 'animation' in description_lower:
                return [
                    "@keyframes ${1:animation-name} {",
                    "  0% {",
                    "    ${2:opacity: 0;}",
                    "  }",
                    "  100% {",
                    "    ${3:opacity: 1;}",
                    "  }",
                    "}",
                    "",
                    ".${4:element} {",
                    "  animation: ${1:animation-name} ${5:1s} ${6:ease-in-out};",
                    "}"
                ]
            elif 'media' in description_lower or 'responsive' in description_lower:
                return [
                    "@media (${1:max-width: 768px}) {",
                    "  .${2:element} {",
                    "    ${3:/* Responsive styles */}",
                    "    ${4:width: 100%;}",
                    "  }",
                    "}"
                ]
            # Default CSS snippet
            return [
                ".${1:selector} {",
                "  ${2:property}: ${3:value};",
                "  ${4:/* Additional styles */}",
                "}"
            ]
        
        # Default snippet for unknown languages
        return [
            "// ${1:" + description + "}",
            "${2:// Insert your code here}"
        ]
    
    def add_snippet(self, snippet: Snippet) -> bool:
        """Add a snippet to the AI-generated collection
        
        Args:
            snippet: Snippet object to add
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            with self.snippet_lock:
                # Initialize language entry if needed
                if snippet.language not in self.ai_snippets:
                    self.ai_snippets[snippet.language] = []
                
                # Check if a snippet with the same name already exists
                for i, existing in enumerate(self.ai_snippets[snippet.language]):
                    if existing.name == snippet.name:
                        # Replace the existing snippet
                        self.ai_snippets[snippet.language][i] = snippet
                        # Save the updated snippets
                        self._save_ai_snippets(snippet.language)
                        return True
                
                # Add new snippet
                self.ai_snippets[snippet.language].append(snippet)
                
                # Save the updated snippets
                self._save_ai_snippets(snippet.language)
                
                return True
        except Exception as e:
            logger.error(f"Error adding AI snippet: {e}")
            return False
    
    def remove_snippet(self, language: str, name: str) -> bool:
        """Remove a snippet from the AI-generated collection
        
        Args:
            language: Language identifier
            name: Name of the snippet to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        try:
            with self.snippet_lock:
                # Check if language exists
                if language not in self.ai_snippets:
                    return False
                
                # Find and remove the snippet
                for i, snippet in enumerate(self.ai_snippets[language]):
                    if snippet.name == name:
                        self.ai_snippets[language].pop(i)
                        # Save the updated snippets
                        self._save_ai_snippets(language)
                        return True
                
                return False
        except Exception as e:
            logger.error(f"Error removing AI snippet: {e}")
            return False
    
    def get_snippets_for_language(self, language: str) -> List[Snippet]:
        """Get all AI-generated snippets for a specific language
        
        Args:
            language: Language identifier
            
        Returns:
            List of Snippet objects
        """
        return self.ai_snippets.get(language, [])
    
    def get_matching_snippets(self, language: str, prefix: str) -> List[Snippet]:
        """Get AI-generated snippets that match a given prefix
        
        Args:
            language: Language identifier
            prefix: Text that might trigger snippets
            
        Returns:
            List of matching Snippet objects
        """
        snippets = self.get_snippets_for_language(language)
        matches = []
        
        for snippet in snippets:
            if snippet.prefix.startswith(prefix):
                matches.append(snippet)
        
        return matches
    
    def create_snippet_from_code(self, 
                               language: str, 
                               code: str, 
                               name: Optional[str] = None,
                               prefix: Optional[str] = None,
                               description: Optional[str] = None) -> Optional[Snippet]:
        """Create a snippet from existing code
        
        Args:
            language: Programming language
            code: The code to convert to a snippet
            name: Optional name for the snippet
            prefix: Optional trigger text for the snippet
            description: Optional description of the snippet
            
        Returns:
            Created Snippet object or None if creation failed
        """
        try:
            # Split code into lines
            code_lines = code.splitlines()
            
            # Remove leading/trailing empty lines
            while code_lines and not code_lines[0].strip():
                code_lines.pop(0)
            while code_lines and not code_lines[-1].strip():
                code_lines.pop()
            
            if not code_lines:
                logger.warning("Cannot create snippet from empty code")
                return None
            
            # Generate a name if not provided
            if not name:
                # Extract name from first line if it's a function/class definition
                first_line = code_lines[0].strip()
                
                # Common patterns
                function_match = re.match(r'(?:function|def|async def)\s+(\w+)', first_line)
                class_match = re.match(r'class\s+(\w+)', first_line)
                
                if function_match:
                    name = function_match.group(1) + " function"
                elif class_match:
                    name = class_match.group(1) + " class"
                else:
                    # Use a generic name based on language
                    name = f"{language.capitalize()} snippet"
            
            # Generate a prefix if not provided
            if not prefix:
                if name:
                    # Use the first word of the name, lowercase
                    prefix = name.split()[0].lower()
                    # Ensure it's a valid identifier
                    prefix = re.sub(r'[^\w]', '', prefix)
                    
                    # Make sure it's not empty
                    if not prefix:
                        prefix = "snippet"
                else:
                    prefix = "snippet"
            
            # Generate a description if not provided
            if not description:
                # Try to extract a description from comments
                for line in code_lines:
                    # Look for comment lines
                    comment_match = re.search(r'(?://|#|/\*|\*|"""|\'\'\')(.+)', line.strip())
                    if comment_match:
                        description = comment_match.group(1).strip()
                        break
                
                # If no description found, use a generic one
                if not description:
                    description = f"Snippet for {name}"
            
            # Create and return the snippet
            if name is None:
                name = "ai_snippet_" + str(int(time.time()))
            snippet = Snippet(name, prefix, code_lines, description, language)
            return snippet
        except Exception as e:
            logger.error(f"Error creating snippet from code: {e}")
            return None

# Singleton instance
_ai_snippet_generator = None

def get_ai_snippet_generator() -> AISnippetGenerator:
    """Get the global AISnippetGenerator instance
    
    Returns:
        AISnippetGenerator instance
    """
    global _ai_snippet_generator
    if _ai_snippet_generator is None:
        _ai_snippet_generator = AISnippetGenerator()
    return _ai_snippet_generator