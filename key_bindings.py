"""
Key Bindings - Defines all keyboard shortcuts for the editor
"""

import os
import re
from prompt_toolkit.filters import has_focus, has_selection, Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyProcessor
from prompt_toolkit.keys import Keys
from editor_core import editor_state, save_file, get_lexer_for_file
from themes import get_available_themes, get_theme_style

# Code completions including snippets
def get_sample_completions(buffer_text, cursor_position):
    """Get sample completions based on context"""
    # In a real implementation, this would analyze the code context
    # and return appropriate completions
    
    # Get the current line and text up to cursor
    current_line = buffer_text.split('\n')[buffer_text.count('\n', 0, cursor_position)]
    text_before_cursor = current_line[:cursor_position - buffer_text.rfind('\n', 0, cursor_position) - 1]
    
    # Check for language context (assuming Python as default)
    language = "python"
    filename = None
    
    if editor_state.get_active_tab():
        filename = editor_state.get_active_tab().filename
        if filename:
            import syntax_styles
            language = syntax_styles.get_language_from_filename(filename)
    
    # Check for snippets that match the current text
    import snippets
    snippet_manager = snippets.get_snippet_manager()
    matching_snippets = []
    
    # Find the last word before cursor (potential snippet trigger)
    word_match = re.search(r'(\w+)$', text_before_cursor)
    if word_match:
        current_word = word_match.group(1)
        matching_snippets = snippet_manager.get_matching_snippets(language, current_word)
    
    # If we have snippets for this context, return them
    if matching_snippets:
        return matching_snippets
    
    # Otherwise, continue with regular text completions
    # Simple check for Python context
    if text_before_cursor.strip().endswith('def '):
        return ['function_name(arg1, arg2)', 'process_data(data)', 'calculate_result(input)']
    elif text_before_cursor.strip().endswith('import '):
        return ['os', 'sys', 'math', 'datetime', 'json', 'random', 'collections']
    elif text_before_cursor.strip().endswith('class '):
        return ['MyClass:', 'DataProcessor:', 'CustomWidget:', 'EventHandler:']
    elif text_before_cursor.strip().endswith('.'):
        # Method completions
        return ['append()', 'extend()', 'sort()', 'pop()', 'remove()', 'count()', 'index()']
    else:
        # General variable/function completions
        completions = ['self', 'data', 'result', 'index', 'value', 'items', 'keys', 'print()', 'len()', 'range()']
        
        # Always add the most common snippets for the language if we have room
        common_snippets = []
        if language == "python":
            if len(matching_snippets) < 3:
                # Add a few Python snippets as examples
                common_snippets = snippet_manager.get_matching_snippets(language, "")
                # Only take the first few to avoid cluttering
                common_snippets = common_snippets[:3]
        
        # Combine regular completions with common snippets
        return completions + common_snippets

def create_key_bindings(terminal_manager):
    """Create key bindings for the application"""
    kb = KeyBindings()
    
    # Toggle auto-save (Alt+A)
    @kb.add('escape', 'a')
    def toggle_auto_save_(event):
        """Toggle auto-save functionality"""
        editor_state.auto_save_enabled = not editor_state.auto_save_enabled
        if editor_state.auto_save_enabled:
            editor_state.status_message = f"Auto-save enabled (every {editor_state.auto_save_interval} seconds)"
        else:
            editor_state.status_message = "Auto-save disabled"
        editor_state.status_type = "info"
        event.app.invalidate()
    
    # Exit application (Ctrl+Q)
    @kb.add('c-q')
    def exit_(event):
        """Exit the application"""
        event.app.exit()
    
    # Save file (Ctrl+S)
    @kb.add('c-s')
    def save_(event):
        """Save the current file"""
        active_tab = editor_state.get_active_tab()
        if active_tab:
            save_file(active_tab.buffer)
            active_tab.modified = False
        event.app.invalidate()
    
    # Toggle terminal visibility (Ctrl+T)
    @kb.add('c-t')
    def toggle_terminal_(event):
        """Toggle terminal visibility"""
        editor_state.show_terminal = not editor_state.show_terminal
        editor_state.status_message = f"Terminal {'shown' if editor_state.show_terminal else 'hidden'}"
        event.app.invalidate()
        
    # New tab (Ctrl+N)
    @kb.add('c-n')
    def new_tab_(event):
        """Create a new tab"""
        new_tab = editor_state.add_tab()
        new_tab.lexer = get_lexer_for_file(None)
        editor_state.status_message = "New tab created"
        event.app.invalidate()
    
    # Close tab (Ctrl+W)
    @kb.add('c-w')
    def close_tab_(event):
        """Close the current tab"""
        if editor_state.close_tab():
            editor_state.status_message = "Tab closed"
        else:
            editor_state.status_message = "Cannot close tab"
        event.app.invalidate()
    
    # Next tab (Ctrl+Right)
    @kb.add('c-right')
    def next_tab_(event):
        """Switch to the next tab"""
        if editor_state.tabs:
            next_index = (editor_state.active_tab_index + 1) % len(editor_state.tabs)
            editor_state.switch_to_tab(next_index)
            active_tab = editor_state.get_active_tab()
            if active_tab and active_tab.filename:
                filename = os.path.basename(active_tab.filename)
                editor_state.status_message = f"Switched to tab {next_index + 1}: {filename}"
            else:
                editor_state.status_message = f"Switched to tab {next_index + 1}"
            event.app.invalidate()
    
    # Previous tab (Ctrl+Left)
    @kb.add('c-left')
    def prev_tab_(event):
        """Switch to the previous tab"""
        if editor_state.tabs:
            prev_index = (editor_state.active_tab_index - 1) % len(editor_state.tabs)
            editor_state.switch_to_tab(prev_index)
            active_tab = editor_state.get_active_tab()
            if active_tab and active_tab.filename:
                filename = os.path.basename(active_tab.filename)
                editor_state.status_message = f"Switched to tab {prev_index + 1}: {filename}"
            else:
                editor_state.status_message = f"Switched to tab {prev_index + 1}"
            event.app.invalidate()
            
    # Switch to tab by number (Alt+1, Alt+2, ...)
    @kb.add('escape', '1')
    def switch_to_tab_1(event):
        _switch_to_tab_n(event, 0)
        
    @kb.add('escape', '2')
    def switch_to_tab_2(event):
        _switch_to_tab_n(event, 1)
        
    @kb.add('escape', '3')
    def switch_to_tab_3(event):
        _switch_to_tab_n(event, 2)
        
    @kb.add('escape', '4')
    def switch_to_tab_4(event):
        _switch_to_tab_n(event, 3)
        
    @kb.add('escape', '5')
    def switch_to_tab_5(event):
        _switch_to_tab_n(event, 4)
        
    @kb.add('escape', '6')
    def switch_to_tab_6(event):
        _switch_to_tab_n(event, 5)
        
    @kb.add('escape', '7')
    def switch_to_tab_7(event):
        _switch_to_tab_n(event, 6)
        
    @kb.add('escape', '8')
    def switch_to_tab_8(event):
        _switch_to_tab_n(event, 7)
        
    @kb.add('escape', '9')
    def switch_to_tab_9(event):
        _switch_to_tab_n(event, 8)
                
    def _switch_to_tab_n(event, index):
        """Switch to tab by number"""
        if 0 <= index < len(editor_state.tabs):
            editor_state.switch_to_tab(index)
            active_tab = editor_state.get_active_tab()
            if active_tab and active_tab.filename:
                filename = os.path.basename(active_tab.filename)
                editor_state.status_message = f"Switched to tab {index + 1}: {filename}"
            else:
                editor_state.status_message = f"Switched to tab {index + 1}"
            event.app.invalidate()
    
    # Execute command (Alt+Enter as a replacement for Shift+Enter)
    @kb.add('escape', 'enter')  # Alt+Enter
    def execute_command_(event):
        """Execute the current line as a shell command"""
        buffer = event.app.current_buffer
        
        # Get the current line text
        current_line = buffer.document.current_line
        
        # Update the editor mode temporarily
        old_mode = editor_state.editor_mode
        editor_state.editor_mode = "COMMAND"
        editor_state.status_message = f"Executing: {current_line}"
        editor_state.status_type = "info"
        event.app.invalidate()
        
        # Ensure terminal is visible
        if not editor_state.show_terminal:
            editor_state.show_terminal = True
        
        # Execute the command
        terminal_manager.execute_command(current_line)
        
        # Move to the next line
        buffer.cursor_down()
        
        # Restore editor mode
        editor_state.editor_mode = old_mode
        event.app.invalidate()
    
    # Clear terminal (Ctrl+L)
    @kb.add('c-l')
    def clear_terminal_(event):
        """Clear the terminal output"""
        terminal_manager.clear_output()
        editor_state.status_message = "Terminal cleared"
        event.app.invalidate()
    
    # Cycle through shells (Ctrl+B as replacement for Ctrl+Shift+S)
    @kb.add('c-b')
    def cycle_shell_(event):
        """Cycle through available shell types"""
        shells = ["bash", "zsh", "cmd"]
        current_shell = terminal_manager.get_current_shell()
        
        # Find the index of the current shell
        try:
            current_index = shells.index(current_shell)
        except ValueError:
            current_index = -1
        
        # Get the next shell in the cycle
        next_index = (current_index + 1) % len(shells)
        next_shell = shells[next_index]
        
        # Change to the next shell
        terminal_manager.change_shell(next_shell)
        editor_state.status_message = f"Switched to {next_shell}"
        event.app.invalidate()
    
    # Toggle AI insights panel (Ctrl+I)
    @kb.add('c-i')
    def toggle_insights_(event):
        """Toggle AI code insights panel"""
        editor_state.toggle_insights()
        editor_state.status_message = f"AI Insights panel {'shown' if editor_state.show_insights else 'hidden'}"
        event.app.invalidate()
    
    # Request AI insight for current code (Alt+I)
    @kb.add('escape', 'i')  # Alt+I
    def analyze_code_(event):
        """Request AI analysis of current code"""
        if editor_state.request_code_insight():
            # Ensure insights panel is visible
            if not editor_state.show_insights:
                editor_state.show_insights = True
        event.app.invalidate()
    
    # Toggle line wrapping (Alt+W)
    @kb.add('escape', 'w')  # Alt+W
    def toggle_wrap_(event):
        """Toggle line wrapping"""
        editor_state.toggle_line_wrap()
        editor_state.status_message = f"Line wrapping {'enabled' if editor_state.wrap_lines else 'disabled'}"
        event.app.invalidate()
    
    # Toggle line numbers (Alt+N)
    @kb.add('escape', 'n')  # Alt+N
    def toggle_line_numbers_(event):
        """Toggle line numbers"""
        editor_state.toggle_line_numbers()
        editor_state.status_message = f"Line numbers {'shown' if editor_state.line_numbers else 'hidden'}"
        event.app.invalidate()
    
    # Toggle code folding (Alt+F)
    @kb.add('escape', 'f')  # Alt+F
    def toggle_folding_(event):
        """Toggle code folding functionality"""
        editor_state.toggle_folding()
        editor_state.status_message = f"Code folding {'enabled' if editor_state.folding_enabled else 'disabled'}"
        event.app.invalidate()
    
    # Toggle fold at cursor (Alt+Z)
    @kb.add('escape', 'z')  # Alt+Z
    def toggle_fold_at_cursor_(event):
        """Toggle fold at the current cursor position"""
        if editor_state.folding_enabled:
            if editor_state.toggle_fold_at_cursor():
                # Status message is set in toggle_fold_at_cursor
                pass
            else:
                editor_state.status_message = "No foldable region at cursor"
                editor_state.status_type = "warning"
        else:
            editor_state.status_message = "Code folding is disabled. Enable with Alt+F first."
            editor_state.status_type = "warning"
        event.app.invalidate()
        
    # Toggle syntax checking (Alt+C)
    @kb.add('escape', 'c')  # Alt+C
    def toggle_syntax_check_(event):
        """Toggle syntax checking functionality"""
        editor_state.toggle_syntax_check()
        # Status message is set in toggle_syntax_check method
        event.app.invalidate()
        
    # Check syntax now (Alt+S)
    @kb.add('escape', 's')  # Alt+S
    def check_syntax_now_(event):
        """Run syntax check on current file immediately"""
        if not editor_state.syntax_check_enabled:
            editor_state.status_message = "Syntax checking is disabled (Alt+C to enable)"
            editor_state.status_type = "warning"
        else:
            editor_state.check_current_file_syntax()
            editor_state.status_message = "Running syntax check..."
            editor_state.status_type = "info"
        event.app.invalidate()
        
    # Toggle search panel (Ctrl+F)
    @kb.add('c-f')
    def toggle_search_(event):
        """Toggle search panel"""
        editor_state.toggle_search_ui()
        editor_state.status_message = f"Search panel {'shown' if editor_state.show_search_ui else 'hidden'}"
        event.app.invalidate()
        
    # Find next (F3)
    @kb.add('f3')
    def find_next_(event):
        """Find the next search result"""
        if editor_state.search_results:
            result = editor_state.goto_next_search_result()
            if result:
                active_tab = editor_state.get_active_tab()
                if active_tab:
                    start, end = result
                    active_tab.buffer.cursor_position = start
                    index = editor_state.current_search_index + 1
                    count = len(editor_state.search_results)
                    editor_state.status_message = f"Match {index} of {count}"
        else:
            editor_state.status_message = "No search results"
            editor_state.status_type = "warning"
        event.app.invalidate()
    
    # Find previous (function without key binding)
    def find_prev_(event):
        """Find the previous search result"""
        if editor_state.search_results:
            result = editor_state.goto_prev_search_result()
            if result:
                active_tab = editor_state.get_active_tab()
                if active_tab:
                    start, end = result
                    active_tab.buffer.cursor_position = start
                    index = editor_state.current_search_index + 1
                    count = len(editor_state.search_results)
                    editor_state.status_message = f"Match {index} of {count}"
        else:
            editor_state.status_message = "No search results"
            editor_state.status_type = "warning"
        event.app.invalidate()
        
    # Find previous (removed Shift+F3 binding as it causes an error in prompt-toolkit 3.0.43)
    # See alternative binding below with Ctrl+F3
        
    # Alternative key binding for find previous (Ctrl+F3)
    # Added for compatibility with prompt-toolkit 3.0.43, as some Shift+F3 implementations may not work correctly
    @kb.add('c-f3')
    def find_prev_alt_(event):
        """Find the previous search result (alternative key binding)"""
        # Call the same function as Shift+F3
        find_prev_(event)
    
    # Toggle tooltips (Alt+H for "hover tips")
    @kb.add('escape', 'h')  # Alt+H
    def toggle_tooltips_(event):
        """Toggle code insight tooltips"""
        if hasattr(editor_state, 'tooltips'):
            editor_state.tooltips.show_tooltips = not editor_state.tooltips.show_tooltips
            editor_state.status_message = f"Code tooltips {'enabled' if editor_state.tooltips.show_tooltips else 'disabled'}"
            editor_state.status_type = "info"
            event.app.invalidate()
    
    # Code completion popup (Ctrl+Space)
    @kb.add('c-space')
    def show_completions_(event):
        """Show code completion popup"""
        buffer = event.app.current_buffer
        cursor_position = buffer.cursor_position
        document = buffer.document
        
        # Get sample completions based on context
        completions = get_sample_completions(document.text, cursor_position)
        
        if completions:
            # Get the cursor position in terms of row and column
            row = document.cursor_position_row
            col = document.cursor_position_col
            
            # Show the completion popup
            editor_state.show_code_completion(completions, (row, col))
            editor_state.status_message = f"Showing {len(completions)} completions"
        else:
            editor_state.status_message = "No completions available"
            editor_state.status_type = "info"
        
        event.app.invalidate()
    
    # Navigate to next completion (Tab)
    @kb.add('tab', filter=Condition(lambda: hasattr(editor_state, 'completion') and 
                                  editor_state.completion.visible and 
                                  not has_selection()))
    def next_completion_(event):
        """Select the next completion option"""
        editor_state.select_next_completion()
        event.app.invalidate()
    
    # Navigate to previous completion (Shift+Tab)
    @kb.add('s-tab', filter=Condition(lambda: hasattr(editor_state, 'completion') and 
                                   editor_state.completion.visible))
    def prev_completion_(event):
        """Select the previous completion option"""
        editor_state.select_prev_completion()
        event.app.invalidate()
    
    # Accept the selected completion (Enter when completion is visible)
    @kb.add('enter', filter=Condition(lambda: hasattr(editor_state, 'completion') and 
                                   editor_state.completion.visible))
    def accept_completion_(event):
        """Accept the currently selected completion"""
        editor_state.accept_selected_completion()
        editor_state.status_message = "Completion applied"
        editor_state.status_type = "info"
        event.app.invalidate()
        
    # Dismiss completion popup (Escape)
    @kb.add('escape', filter=Condition(lambda: hasattr(editor_state, 'completion') and 
                                    editor_state.completion.visible))
    def dismiss_completion_(event):
        """Dismiss the completion popup"""
        editor_state.hide_code_completion()
        editor_state.status_message = "Completion canceled"
        editor_state.status_type = "info"
        event.app.invalidate()
        
    # Navigate to next snippet placeholder (Tab)
    @kb.add('tab', filter=Condition(lambda: hasattr(editor_state, 'completion') and 
                                 editor_state.completion.is_snippet))
    def next_snippet_placeholder_(event):
        """Navigate to the next snippet placeholder"""
        if editor_state.navigate_next_snippet_placeholder():
            event.app.invalidate()
        
    # Navigate to previous snippet placeholder (Shift+Tab)
    @kb.add('s-tab', filter=Condition(lambda: hasattr(editor_state, 'completion') and 
                                   editor_state.completion.is_snippet))
    def prev_snippet_placeholder_(event):
        """Navigate to the previous snippet placeholder"""
        if editor_state.navigate_prev_snippet_placeholder():
            event.app.invalidate()
            
    # Exit snippet mode (Escape when in snippet mode)
    @kb.add('escape', filter=Condition(lambda: hasattr(editor_state, 'completion') and 
                                    editor_state.completion.is_snippet and 
                                    not editor_state.completion.visible))
    def exit_snippet_mode_(event):
        """Exit snippet mode if active"""
        editor_state.completion.is_snippet = False
        editor_state.completion.active_snippet = None
        editor_state.completion.snippet_placeholders = []
        editor_state.completion.current_placeholder = 0
        
        # Remove any selection
        active_tab = editor_state.get_active_tab()
        if active_tab and active_tab.buffer:
            active_tab.buffer.selection_state = None
            
    # Create AI snippet from selected code (Alt+G)
    @kb.add('escape', 'g', filter=has_selection)
    def create_ai_snippet_(event):
        """Create an AI-generated snippet from selected text"""
        # Get the selected text
        buffer = event.current_buffer
        
        # Extract selected text from the buffer
        if buffer.selection_state:
            start, end = buffer.document.translate_index_to_position(buffer.selection_state.original_cursor_position)
            cursor_pos_row, cursor_pos_col = buffer.document.translate_index_to_position(buffer.cursor_position)
            
            # Determine start and end based on selection direction
            from_row, from_col = min(start, cursor_pos_row), 0 if start != cursor_pos_row else min(end, cursor_pos_col)
            to_row, to_col = max(start, cursor_pos_row), 0 if start != cursor_pos_row else max(end, cursor_pos_col)
            
            lines = buffer.document.lines
            selected_text = ""
            
            # Extract text from the selection
            for i in range(from_row, to_row + 1):
                if i < len(lines):
                    line = lines[i]
                    start_col = from_col if i == from_row else 0
                    end_col = to_col if i == to_row else len(line)
                    if start_col <= len(line) and end_col <= len(line):
                        selected_text += line[start_col:end_col]
                    if i < to_row:
                        selected_text += "\n"
        else:
            selected_text = ""
        
        if not selected_text:
            editor_state.status_message = "No text selected"
            editor_state.status_type = "error"
            return
        
        # Determine language from current file
        language = "text"  # Default language
        if editor_state.get_active_tab() and editor_state.get_active_tab().filename:
            filename = editor_state.get_active_tab().filename
            import syntax_styles
            language = syntax_styles.get_language_from_filename(filename)
        
        # Import AI snippet generator
        import ai_snippets
        ai_snippet_generator = ai_snippets.get_ai_snippet_generator()
        
        # Show a message in the status bar
        editor_state.status_message = "Creating AI snippet..."
        editor_state.status_type = "info"
        event.app.invalidate()
        
        # Create snippet from selected code
        snippet = ai_snippet_generator.create_snippet_from_code(
            language=language,
            code=selected_text
        )
        
        if snippet:
            # Add to the AI snippet collection
            success = ai_snippet_generator.add_snippet(snippet)
            
            if success:
                editor_state.status_message = f"AI Snippet '{snippet.name}' created! Trigger with '{snippet.prefix}'"
                editor_state.status_type = "info"
            else:
                editor_state.status_message = "Failed to save AI snippet"
                editor_state.status_type = "error"
        else:
            editor_state.status_message = "Failed to create AI snippet"
            editor_state.status_type = "error"
        
        # Refresh the UI
        event.app.invalidate()
            
        editor_state.status_message = "Exited snippet mode"
        editor_state.status_type = "info"
        event.app.invalidate()
    
    # Cycle editor theme (Alt+T)
    @kb.add('escape', 't')  # Alt+T
    def cycle_theme_(event):
        """Cycle through available editor themes"""
        new_theme = editor_state.cycle_theme()
        editor_state.status_message = f"Theme changed to {new_theme}"
        
        # Force a full redraw of the UI to apply the theme
        event.app.style = get_theme_style(new_theme)
        event.app.invalidate()
    
    # Help screen (F1)
    @kb.add('f1')
    def show_help_(event):
        """Show the help screen"""
        help_text = [
            "TextShellEditor Keyboard Shortcuts:",
            "",
            "Ctrl+Q        - Exit the application",
            "Ctrl+S        - Save the current file",
            "Ctrl+T        - Toggle terminal visibility",
            "Alt+Enter     - Execute the current line as a command",
            "Ctrl+L        - Clear the terminal output",
            "Ctrl+B        - Cycle through available shells",
            "F1            - Show this help screen",
            "",
            "Tab Management:",
            "Ctrl+N        - Create a new tab",
            "Ctrl+W        - Close the current tab",
            "Ctrl+Right    - Switch to the next tab",
            "Ctrl+Left     - Switch to the previous tab",
            "Alt+1 to Alt+9 - Switch to a specific tab by number",
            "",
            "Appearance:",
            "Alt+T         - Cycle through editor themes",
            "",
            "AI Features:",
            "Ctrl+I        - Toggle AI code insights panel",
            "Alt+I         - Analyze current code at cursor position",
            "Alt+H         - Toggle code insight tooltips",
            "Ctrl+Space    - Show code completion suggestions",
            "Tab/Shift+Tab - Navigate through completion options",
            "Enter         - Accept selected completion",
            "Escape        - Cancel completion",
            "",
            "Snippets:",
            "Tab           - Insert snippet or navigate to next placeholder",
            "Shift+Tab     - Navigate to previous placeholder",
            "Escape        - Exit snippet mode",
            "Alt+G         - Create AI snippet from selected code",
            "",
            "Editor View:",
            "Alt+W        - Toggle line wrapping",
            "Alt+N        - Toggle line numbers",
            "Alt+A        - Toggle auto-save feature",
            "Alt+F        - Toggle code folding",
            "Alt+Z        - Toggle fold at cursor position",
            "Alt+C        - Toggle syntax checking",
            "Alt+S        - Check syntax on current file",
            "",
            "Search & Replace:",
            "Ctrl+F       - Toggle search panel",
            "F3           - Find next match",
            "Ctrl+F3      - Find previous match (Shift+F3 not supported in this version)"
        ]
        # Join the help text and display it
        terminal_manager.clear_output()
        for line in help_text:
            terminal_manager._append_output(line, output_type="info")
        
        # Make sure terminal is visible
        editor_state.show_terminal = True
        editor_state.status_message = "Help displayed in terminal"
        event.app.invalidate()
    
    return kb
