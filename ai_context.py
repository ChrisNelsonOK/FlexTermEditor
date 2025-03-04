"""
AI Context - Provides AI-powered code analysis and contextual insights
"""

import re
import sys
import threading
import time
from collections import deque

# Cache for storing insights to avoid regenerating the same content
insights_cache = {}
# Queue for storing analysis requests
analysis_queue = deque()
# Flag to track if an analysis is currently running
is_analyzing = False
# Lock for thread safety
analysis_lock = threading.Lock()

def get_code_context(text, line_number):
    """Extract relevant context from the code around the current line"""
    lines = text.split('\n')
    if not lines or line_number >= len(lines):
        return None
    
    # Get the current line
    current_line = lines[line_number].strip()
    
    # If the line is empty, there's no context to analyze
    if not current_line:
        return None
    
    # Determine the start and end of the context window
    # Try to get 5 lines before and after for context
    context_start = max(0, line_number - 5)
    context_end = min(len(lines), line_number + 6)
    
    # Extract the context lines
    context_lines = lines[context_start:context_end]
    context_text = '\n'.join(context_lines)
    
    # Determine what kind of code context we're looking at
    context_type = determine_context_type(current_line, context_text)
    
    return {
        'line_number': line_number,
        'current_line': current_line,
        'context_text': context_text,
        'context_type': context_type
    }

def determine_context_type(current_line, context_text):
    """Try to determine what kind of code construct we're looking at"""
    # Check for function/method definition
    if re.search(r'def\s+\w+\s*\(', current_line):
        return 'function_definition'
    
    # Check for class definition
    if re.search(r'class\s+\w+', current_line):
        return 'class_definition'
    
    # Check for loop construct
    if re.search(r'for\s+\w+\s+in\s+', current_line) or re.search(r'while\s+', current_line):
        return 'loop_construct'
    
    # Check for conditional
    if re.search(r'if\s+', current_line) or re.search(r'elif\s+', current_line) or re.search(r'else\s*:', current_line):
        return 'conditional'
    
    # Check for import statement
    if re.search(r'import\s+', current_line) or re.search(r'from\s+\w+\s+import', current_line):
        return 'import_statement'
    
    # Check for variable assignment
    if '=' in current_line and not re.search(r'==|!=|<=|>=|\+=|-=|\*=|/=', current_line):
        return 'variable_assignment'
    
    # Default to general code
    return 'general_code'

def generate_insight(context):
    """Generate AI-powered insights based on the code context"""
    if not context:
        return "No context available for analysis."
    
    context_type = context['context_type']
    current_line = context['current_line']
    context_text = context['context_text']
    filename = context.get('filename')
    
    # Add filename to context key if available to make insights more specific
    cache_key = f"{context_text}:{context_type}:{filename if filename else ''}"
    if cache_key in insights_cache:
        return insights_cache[cache_key]
    
    # Enhanced rule-based insights based on context type
    try:
        if context_type == 'function_definition':
            insight = generate_function_insight(context_text)
            # Add complexity estimation
            complexity = estimate_function_complexity(context_text)
            if complexity:
                insight += f" {complexity}"
        elif context_type == 'class_definition':
            insight = generate_class_insight(context_text)
            # Add class relationship suggestions
            relationships = suggest_class_relationships(context_text)
            if relationships:
                insight += f" {relationships}"
        elif context_type == 'loop_construct':
            insight = generate_loop_insight(context_text, current_line)
            # Add performance tips for loops
            perf_tip = suggest_loop_optimization(context_text)
            if perf_tip:
                insight += f" {perf_tip}"
        elif context_type == 'conditional':
            insight = generate_conditional_insight(context_text)
            # Add potential simplification suggestions
            simplification = suggest_conditional_simplification(context_text)
            if simplification:
                insight += f" {simplification}"
        elif context_type == 'import_statement':
            insight = generate_import_insight(current_line)
            # Add import best practices
            best_practice = suggest_import_best_practice(current_line)
            if best_practice:
                insight += f" {best_practice}"
        elif context_type == 'variable_assignment':
            insight = generate_variable_insight(current_line, context_text)
            # Add type hints or naming suggestions
            naming_tip = suggest_variable_naming(current_line)
            if naming_tip:
                insight += f" {naming_tip}"
        else:
            insight = generate_general_insight(context_text)
    except Exception as e:
        # Fallback to simpler insight generation if enhanced version fails
        print(f"Error in enhanced insight generation: {str(e)}", file=sys.stderr)
        insight = f"Code analysis completed. {context_type.replace('_', ' ').title()} detected."
    
    # Store in cache
    insights_cache[cache_key] = insight
    
    return insight

def estimate_function_complexity(context_text):
    """Estimate function complexity and suggest improvements"""
    # Count the number of branches (if/else statements)
    branches = len(re.findall(r'\bif\b|\belif\b|\belse\b', context_text))
    
    # Count the number of loops
    loops = len(re.findall(r'\bfor\b|\bwhile\b', context_text))
    
    # Count the number of returns
    returns = len(re.findall(r'\breturn\b', context_text))
    
    complexity = branches + loops
    
    if complexity > 5:
        return "High complexity detected. Consider refactoring into smaller functions."
    elif complexity > 3:
        return "Moderate complexity. Function may benefit from simplification."
    elif returns > 2:
        return "Multiple return points detected. Consider consolidating returns."
    
    return ""

def suggest_class_relationships(context_text):
    """Suggest potential class relationships or design patterns"""
    # Look for manager/controller type patterns
    if re.search(r'Manager|Controller|Service', context_text):
        return "This appears to be a service/controller class. Consider dependency injection for better testability."
    
    # Look for data container patterns
    if len(re.findall(r'def __init__', context_text)) == 1 and len(re.findall(r'def \w+', context_text)) <= 3:
        return "This looks like a data container class. Consider using dataclasses or attrs for cleaner implementation."
    
    # Look for inheritance
    if re.search(r'class \w+\((\w+)\):', context_text):
        return "Uses inheritance. Ensure the class follows the Liskov Substitution Principle."
    
    return ""

def suggest_loop_optimization(context_text):
    """Suggest loop optimizations"""
    # Check for nested loops which might be optimized
    if re.search(r'for.*\n.*for', context_text):
        return "Nested loops detected. Consider performance implications for large datasets."
    
    # Check for list comprehension opportunities
    if re.search(r'for\s+\w+\s+in\s+\w+:.*append', context_text):
        return "Consider using a list comprehension for cleaner code and potentially better performance."
    
    # Check for inefficient operation in a loop
    if re.search(r'for.*in range.*:.*\.append', context_text):
        return "If possible, pre-allocate the list size rather than growing it with append."
    
    return ""

def suggest_conditional_simplification(context_text):
    """Suggest simplifications for conditionals"""
    # Check for potential truth value testing simplification
    if re.search(r'if\s+\w+\s*==\s*True', context_text) or re.search(r'if\s+\w+\s*==\s*False', context_text):
        return "Consider simplifying boolean comparisons (use 'if var:' instead of 'if var == True:')."
    
    # Check for potentially complex conditionals
    if re.search(r'if.*and.*and.*and|if.*or.*or.*or', context_text):
        return "Complex condition detected. Consider breaking it down or extracting to a predicate function."
    
    return ""

def suggest_import_best_practice(current_line):
    """Suggest import best practices"""
    # Check for wildcard imports
    if re.search(r'from\s+\w+\s+import\s+\*', current_line):
        return "Wildcard imports are generally discouraged as they can lead to namespace pollution."
    
    # Check for too many imports from one module
    if re.search(r'from\s+\w+\s+import\s+\w+,\s+\w+,\s+\w+,\s+\w+', current_line):
        return "Consider importing the module itself if using many of its components."
    
    # Check for aliased imports
    if re.search(r'import\s+\w+\s+as\s+\w+', current_line):
        return "Using alias. Make sure the alias is clear and follows project conventions."
    
    return ""

def suggest_variable_naming(current_line):
    """Suggest variable naming improvements"""
    # Extract variable name from assignment
    var_match = re.search(r'(\w+)\s*=', current_line)
    if not var_match:
        return ""
    
    var_name = var_match.group(1)
    
    # Check for single-letter variables (except common ones like i, j, k for loops)
    if len(var_name) == 1 and var_name not in ['i', 'j', 'k', 'x', 'y', 'z']:
        return "Consider using a more descriptive variable name."
    
    # Check for snake_case in Python
    if not re.match(r'^[a-z][a-z0-9_]*$', var_name) and not re.match(r'^[A-Z][A-Z0-9_]*$', var_name):
        return "Variable name doesn't follow snake_case (for variables) or UPPER_CASE (for constants) convention."
    
    # Check for very long variable names
    if len(var_name) > 30:
        return "Variable name is very long. Consider a more concise name."
    
    return ""

def generate_function_insight(context_text):
    """Generate insights for function definitions"""
    # Extract function name and parameters
    match = re.search(r'def\s+(\w+)\s*\((.*?)\):', context_text, re.DOTALL)
    if not match:
        return "This appears to be a function definition."
    
    func_name = match.group(1)
    params = match.group(2).strip()
    
    # Check for docstring
    has_docstring = '"""' in context_text or "'''" in context_text
    docstring_note = " It includes a docstring." if has_docstring else " It doesn't have a docstring."
    
    # Check for return statement
    has_return = 'return ' in context_text
    return_note = " It has an explicit return statement." if has_return else " No explicit return statement found."
    
    param_list = params.split(',')
    if params and len(param_list) > 0:
        param_count = len(param_list)
        param_note = f" It takes {param_count} parameter{'s' if param_count > 1 else ''}."
    else:
        param_note = " It doesn't take any parameters."
    
    return f"Function '{func_name}' defined.{param_note}{docstring_note}{return_note}"

def generate_class_insight(context_text):
    """Generate insights for class definitions"""
    # Extract class name and inheritance
    match = re.search(r'class\s+(\w+)(?:\s*\((.*?)\))?:', context_text, re.DOTALL)
    if not match:
        return "This appears to be a class definition."
    
    class_name = match.group(1)
    inheritance = match.group(2).strip() if match.group(2) else None
    
    # Check for methods
    method_count = len(re.findall(r'def\s+\w+\s*\(self', context_text))
    method_note = f" It has {method_count} method{'s' if method_count != 1 else ''}." if method_count > 0 else " No methods defined yet."
    
    # Check for docstring
    has_docstring = '"""' in context_text or "'''" in context_text
    docstring_note = " It includes a class docstring." if has_docstring else " It doesn't have a class docstring."
    
    inheritance_note = f" It inherits from {inheritance}." if inheritance else " It doesn't inherit from any class."
    
    return f"Class '{class_name}' defined.{inheritance_note}{method_note}{docstring_note}"

def generate_loop_insight(context_text, current_line):
    """Generate insights for loop constructs"""
    if 'for ' in current_line:
        match = re.search(r'for\s+(\w+)\s+in\s+(.*?):', current_line)
        if match:
            var_name = match.group(1)
            iterable = match.group(2).strip()
            return f"For loop iterating over {iterable} using variable {var_name}."
        return "For loop construct."
    
    if 'while ' in current_line:
        match = re.search(r'while\s+(.*?):', current_line)
        if match:
            condition = match.group(1).strip()
            return f"While loop with condition: {condition}"
        return "While loop construct."
    
    return "Loop construct."

def generate_conditional_insight(context_text):
    """Generate insights for conditional statements"""
    conditions = []
    
    # Find all condition blocks
    if_match = re.search(r'if\s+(.*?):', context_text)
    if if_match:
        conditions.append(f"if {if_match.group(1).strip()}")
    
    elif_matches = re.findall(r'elif\s+(.*?):', context_text)
    for match in elif_matches:
        conditions.append(f"elif {match.strip()}")
    
    has_else = 'else:' in context_text
    if has_else:
        conditions.append("else block")
    
    if len(conditions) > 1:
        return f"Conditional structure with {len(conditions)} branches: {', '.join(conditions)}."
    elif len(conditions) == 1:
        return f"Conditional statement: {conditions[0]}."
    
    return "Conditional statement."

def generate_import_insight(current_line):
    """Generate insights for import statements"""
    if 'from ' in current_line and ' import ' in current_line:
        match = re.search(r'from\s+([\w.]+)\s+import\s+(.*)', current_line)
        if match:
            module = match.group(1)
            imports = match.group(2).strip()
            return f"Importing {imports} from module {module}."
    
    if 'import ' in current_line:
        match = re.search(r'import\s+(.*)', current_line)
        if match:
            imports = match.group(1).strip()
            if ' as ' in imports:
                parts = imports.split(' as ')
                return f"Importing module {parts[0]} with alias {parts[1]}."
            return f"Importing module {imports}."
    
    return "Import statement."

def generate_variable_insight(current_line, context_text):
    """Generate insights for variable assignments"""
    match = re.search(r'(\w+)\s*=\s*(.*)', current_line)
    if not match:
        return "Variable assignment."
    
    var_name = match.group(1)
    value = match.group(2).strip()
    
    # Try to determine the type of the value
    value_type = "value"
    if value.startswith('"') or value.startswith("'"):
        value_type = "string"
    elif value.isdigit():
        value_type = "integer"
    elif value.replace('.', '', 1).isdigit():
        value_type = "float"
    elif value in ['True', 'False']:
        value_type = "boolean"
    elif value.startswith('[') and value.endswith(']'):
        value_type = "list"
    elif value.startswith('{') and value.endswith('}'):
        value_type = "dictionary" if ':' in value else "set"
    elif value.startswith('(') and value.endswith(')'):
        value_type = "tuple"
    elif '(' in value and ')' in value:
        value_type = "function call result"
    
    return f"Variable '{var_name}' assigned a {value_type}."

def generate_general_insight(context_text):
    """Generate insights for general code"""
    # Count the number of lines
    line_count = len(context_text.split('\n'))
    
    # Identify common patterns
    has_comments = '#' in context_text
    comment_note = " Contains inline comments." if has_comments else ""
    
    has_function_calls = re.search(r'\w+\s*\(', context_text) is not None
    call_note = " Contains function calls." if has_function_calls else ""
    
    return f"General code block with {line_count} lines.{comment_note}{call_note}"

def request_analysis(text, line_number, filename=None):
    """Request code analysis for the given text and line"""
    with analysis_lock:
        # Add to queue
        analysis_queue.append((text, line_number, filename))
        
        # Start analysis thread if not already running
        global is_analyzing
        if not is_analyzing:
            is_analyzing = True
            threading.Thread(target=process_analysis_queue, daemon=True).start()
            
    return "Analysis requested..."

def process_analysis_queue():
    """Process the analysis queue in a background thread"""
    global is_analyzing, latest_insight
    
    try:
        while True:
            # Check if there are items in the queue
            with analysis_lock:
                if not analysis_queue:
                    is_analyzing = False
                    break
                
                # Get the next item
                text, line_number, filename = analysis_queue.popleft()
            
            # Generate the insight outside the lock to prevent blocking
            try:
                context = get_code_context(text, line_number)
                if context:
                    # Append the filename to the context if available
                    if filename:
                        context['filename'] = filename
                        
                    # Generate the insight
                    insight = generate_insight(context)
                    
                    # Store in global variable that can be accessed by the editor
                    # Using the lock to ensure thread-safe update
                    with analysis_lock:
                        latest_insight = insight
                    
                    # Simulate some processing time
                    time.sleep(0.5)
            except Exception as e:
                # In case of error, log it and continue
                print(f"Error generating insight: {str(e)}", file=sys.stderr)
    finally:
        # Ensure we reset the flag when done, even if an exception occurs
        with analysis_lock:
            is_analyzing = False

# Initialize the latest insight
latest_insight = None

def get_latest_insight():
    """Get the latest generated insight in a thread-safe manner"""
    with analysis_lock:
        return latest_insight