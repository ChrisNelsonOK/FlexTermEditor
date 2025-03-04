"""
Editor Core - Main editor functionality and layout creation
"""

import os
import re
import sys
import threading
import time

def get_fragment_line(fragment, transformation_input):
    """
    Get the line number for a fragment in a compatible way.
    In pt 3.0.43, fragments are tuples, not objects with a 'line' attribute.
    """
    # For newer versions of prompt-toolkit where fragments are tuples
    if not hasattr(fragment, 'line'):
        # Default to current line from transformation input
        return transformation_input.lineno
    # For older versions where fragments have a line attribute
    return fragment.line
# Import AI context module
import ai_context
# Import auto-indent functionality
import auto_indent
# Import syntax checking
import syntax_checker
# Import enhanced syntax highlighting
import syntax_styles
# Import snippets
import snippets
# Import correct prompt_toolkit modules
# Handle different prompt_toolkit versions
try:
    # For prompt_toolkit 3.x
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.document import Document
    from prompt_toolkit.filters import Condition
    from prompt_toolkit.layout.containers import (
        HSplit, VSplit, Window, WindowAlign, 
        ConditionalContainer, DynamicContainer
    )
    from prompt_toolkit.layout.controls import (
        BufferControl, FormattedTextControl
    )
    from prompt_toolkit.layout.margins import NumberedMargin
    from prompt_toolkit.layout.processors import HighlightMatchingBracketProcessor, Processor, Transformation
    from prompt_toolkit.lexers import PygmentsLexer
    from prompt_toolkit.layout.layout import Layout
    from prompt_toolkit.widgets import Frame, TextArea, Button, Checkbox
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.formatted_text import Fragment
    from prompt_toolkit.selection import SelectionState
    from prompt_toolkit.application import get_app as editor_app
except ImportError:
    # For prompt_toolkit 2.x
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.document import Document
    from prompt_toolkit.filters import Condition
    from prompt_toolkit.layout import (
        HSplit, VSplit, Window, WindowAlign, 
        ConditionalContainer, DynamicContainer
    )
    from prompt_toolkit.layout.controls import (
        BufferControl, FormattedTextControl
    )
    from prompt_toolkit.layout.margins import NumberedMargin
    from prompt_toolkit.layout.processors import HighlightMatchingBracketProcessor
    from prompt_toolkit.lexers import PygmentsLexer
    from prompt_toolkit.layout import Layout
    from prompt_toolkit.widgets import Frame, TextArea

from pygments.lexers import get_lexer_for_filename, TextLexer
from pygments.util import ClassNotFound

class EditorTab:
    """Represents a single editor tab"""
    def __init__(self, filename=None, buffer=None):
        self.filename = filename
        self.buffer = buffer or Buffer()
        self.modified = False
        self.lexer = None  # Will be set after get_lexer_for_file is defined
        # File loading will be done after initialization

class EditorState:
    """Global state for the editor application"""
    def __init__(self):
        self.tabs = []
        self.active_tab_index = 0
        self.status_message = ""
        self.status_type = "info"  # info, warning, error
        self.editor_mode = "EDIT"  # EDIT, COMMAND, SEARCH
        self.show_terminal = True
        self.show_insights = True  # Toggle for AI insights panel
        self.analyzing_code = False  # Flag to track if analysis is in progress
        self.current_insight = None  # Current insight text
        self.wrap_lines = True  # Toggle for line wrapping
        self.line_numbers = True  # Toggle for line numbers
        
        # Search functionality
        self.search_query = ""
        self.search_results = []
        self.current_search_index = 0
        self.replace_text = ""
        self.show_search_ui = False
        
        # Auto-save functionality
        self.auto_save_enabled = True
        self.auto_save_interval = 30  # in seconds
        self.last_save_time = {}  # Map of filenames to last save time
        
        # Syntax checking
        self.syntax_check_enabled = True  # Toggle for syntax checking
        self.check_on_save = True  # Check syntax when saving
        self.syntax_errors = {}  # Map of filenames to lists of syntax errors
        
        # Code folding
        self.folding_enabled = True  # Toggle for code folding
        self.folded_regions = {}  # Map of filenames to lists of folded regions (start_line, end_line)
        
        # Terminal configuration
        self.terminal_height = 8  # rows
        
        # Indentation settings
        self.tab_size = 4  
        self.use_spaces = True  # Use spaces instead of tabs
        
        # Theme settings
        self.current_theme = 'dracula'  # Default theme
        
        # Animation settings
        self.enable_animations = True  # Toggle for animation features
        
        # Initialize code completion state
        # This will be properly initialized once the CompletionState class is defined
        self.completion = None
        
        # Initialize animation and tooltip properties
        # These will be properly set later when the respective classes are defined
        self.tab_animation = None  # Will hold TabAnimationState instance
        self.tooltips = None  # Will hold InsightTooltipState instance
        
        # Micro-animation properties
        self.button_states = {}  # Tracking button animation states
        self.toggle_states = {}  # Tracking toggle animation states
        self.panel_focus_states = {}  # Tracking panel focus states
        self.notification_states = {}  # Tracking notification states
        
        # Panel animation properties
        self.insights_panel_opacity = 1.0
        self.search_panel_opacity = 1.0
        self.terminal_panel_opacity = 1.0
        
        # Animation refresh flag
        self.refresh_required = False
        
    def toggle_syntax_check(self):
        """Toggle syntax checking functionality"""
        # Toggle the state
        self.syntax_check_enabled = not self.syntax_check_enabled
        
        # Import micro_animations here to avoid circular imports
        if self.enable_animations:
            import micro_animations
            
            # Create a toggle state object if it doesn't exist
            toggle_id = "syntax_check"
            if toggle_id not in self.toggle_states:
                self.toggle_states[toggle_id] = type('ToggleState', (), {'highlight': 0.0})
                
            # Animate the toggle effect
            micro_animations.get_micro_animations().animate_toggle(
                self.toggle_states[toggle_id], 
                self.syntax_check_enabled
            )
            
        # If enabled, trigger a check of the current file
        if self.syntax_check_enabled:
            self.check_current_file_syntax()
            self.status_message = "Syntax checking enabled"
        else:
            self.status_message = "Syntax checking disabled"
            
        self.status_type = "info"
        return self.syntax_check_enabled
        
    def check_current_file_syntax(self):
        """Request syntax check for the current file"""
        if not self.syntax_check_enabled:
            return False
            
        active_tab = self.get_active_tab()
        if not active_tab or not active_tab.buffer:
            return False
            
        # Get the text and request a syntax check
        text = active_tab.buffer.text
        syntax_checker.request_syntax_check(text, active_tab.filename)
        
        # Schedule retrieval of results after a delay
        def retrieve_syntax_results():
            filename = active_tab.filename
            self.syntax_errors[filename] = syntax_checker.get_syntax_errors(filename)
            
            if self.syntax_errors[filename]:
                error_count = len(self.syntax_errors[filename])
                self.status_message = f"Found {error_count} syntax/style issue{'s' if error_count != 1 else ''}"
                self.status_type = "error"
            else:
                self.status_message = "No syntax issues found"
                self.status_type = "info"
        
        # Start a thread to retrieve results after a short delay
        threading.Timer(0.5, retrieve_syntax_results).start()
        
        return True

    def add_tab(self, filename=None):
        """Add a new tab and make it active"""
        new_tab = EditorTab(filename=filename)
        self.tabs.append(new_tab)
        self.active_tab_index = len(self.tabs) - 1
        return new_tab

    def close_tab(self, index=None):
        """Close the tab at the given index or the active tab if none specified"""
        if not self.tabs:
            return False
        
        if index is None:
            index = self.active_tab_index
        
        if 0 <= index < len(self.tabs):
            del self.tabs[index]
            
            # Update active tab index if needed
            if self.tabs:
                self.active_tab_index = min(index, len(self.tabs) - 1)
            else:
                # No tabs left, add an empty one
                self.add_tab()
            return True
        return False

    def switch_to_tab(self, index):
        """Switch to the tab at the given index"""
        if 0 <= index < len(self.tabs):
            old_index = self.active_tab_index
            self.active_tab_index = index
            
            # Start tab transition animation
            animate_tab_transition(old_index, index)
            
            return True
        return False
    
    def get_active_tab(self):
        """Get the currently active tab"""
        if self.tabs and 0 <= self.active_tab_index < len(self.tabs):
            return self.tabs[self.active_tab_index]
        return None
    
    def toggle_insights(self):
        """Toggle the AI insights panel visibility"""
        # Toggle the state
        self.show_insights = not self.show_insights
        
        # Import micro_animations here to avoid circular imports
        if self.enable_animations:
            import micro_animations
            
            # Create a toggle state object if it doesn't exist
            toggle_id = "insights_panel"
            if toggle_id not in self.toggle_states:
                self.toggle_states[toggle_id] = type('ToggleState', (), {'highlight': 0.0})
                
            # Animate the toggle effect
            micro_animations.get_micro_animations().animate_toggle(
                self.toggle_states[toggle_id], 
                self.show_insights
            )
            
            # Animate panel opacity
            if self.show_insights:
                # Start at 0 and animate to 1
                self.insights_panel_opacity = 0.0
                
                # Create and start a fade-in animation
                class PanelFadeIn(animations.AnimationState):
                    def __init__(self, target):
                        super().__init__()
                        self.target = target
                        self.duration = 0.25
                        
                    def on_frame(self):
                        progress = self.get_eased_progress("ease_out_cubic")
                        self.target.insights_panel_opacity = progress
                        refresh_editor_view()
                
                fade_in = PanelFadeIn(self)
                animations.animation_manager.add_animation("insights_panel_fade", fade_in)
                animations.animation_manager.start_animation("insights_panel_fade")
            
        return self.show_insights
        
    def toggle_line_wrap(self):
        """Toggle line wrapping in the editor"""
        # Toggle the state
        self.wrap_lines = not self.wrap_lines
        
        # Import micro_animations here to avoid circular imports
        if self.enable_animations:
            import micro_animations
            
            # Create a toggle state object if it doesn't exist
            toggle_id = "line_wrap"
            if toggle_id not in self.toggle_states:
                self.toggle_states[toggle_id] = type('ToggleState', (), {'highlight': 0.0})
                
            # Animate the toggle effect
            micro_animations.get_micro_animations().animate_toggle(
                self.toggle_states[toggle_id], 
                self.wrap_lines
            )
            
        return self.wrap_lines
        
    def toggle_line_numbers(self):
        """Toggle line numbers in the editor"""
        # Toggle the state
        self.line_numbers = not self.line_numbers
        
        # Import micro_animations here to avoid circular imports
        if self.enable_animations:
            import micro_animations
            
            # Create a toggle state object if it doesn't exist
            toggle_id = "line_numbers"
            if toggle_id not in self.toggle_states:
                self.toggle_states[toggle_id] = type('ToggleState', (), {'highlight': 0.0})
                
            # Animate the toggle effect
            micro_animations.get_micro_animations().animate_toggle(
                self.toggle_states[toggle_id], 
                self.line_numbers
            )
            
        return self.line_numbers
        
    def toggle_folding(self):
        """Toggle code folding in the editor"""
        # Toggle the state
        self.folding_enabled = not self.folding_enabled
        
        # Import micro_animations here to avoid circular imports
        if self.enable_animations:
            import micro_animations
            
            # Create a toggle state object if it doesn't exist
            toggle_id = "folding"
            if toggle_id not in self.toggle_states:
                self.toggle_states[toggle_id] = type('ToggleState', (), {'highlight': 0.0})
                
            # Animate the toggle effect
            micro_animations.get_micro_animations().animate_toggle(
                self.toggle_states[toggle_id], 
                self.folding_enabled
            )
            
        return self.folding_enabled
        
    def show_code_completion(self, completions, position):
        """Show the code completion popup
        
        Args:
            completions (list): List of completion string options
            position (tuple): (row, column) position where the popup should appear
        """
        # If already showing completions, hide first
        if self.completion.visible:
            self.hide_code_completion()
        
        # Get current file to determine language for snippets
        active_tab = self.get_active_tab()
        if active_tab and active_tab.filename:
            import os
            from utils import get_file_extension
            file_ext = get_file_extension(active_tab.filename)
            
            # Map file extension to language identifier
            language_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.html': 'html',
                '.css': 'css',
                '.java': 'java',
                '.c': 'c',
                '.cpp': 'cpp',
                '.h': 'c',
                '.hpp': 'cpp',
                '.go': 'go',
                '.rb': 'ruby',
                '.php': 'php',
                '.rs': 'rust',
                '.sh': 'shell',
                '.md': 'markdown',
                '.xml': 'xml',
                '.json': 'json',
                '.sql': 'sql',
                '.yaml': 'yaml',
                '.yml': 'yaml',
            }
            
            language = language_map.get(file_ext.lower(), 'text')
            
            # Get current line and cursor position to check for snippet triggers
            if active_tab.buffer:
                cursor_position = active_tab.buffer.cursor_position
                document = active_tab.buffer.document
                cursor_line = document.cursor_position_row
                line = document.lines[cursor_line]
                
                # Get text before cursor (potential snippet prefix)
                line_before_cursor = line[:document.cursor_position_col]
                word_before_cursor = ''
                
                # Extract the last word before cursor (potential snippet trigger)
                import re
                match = re.search(r'[\w_]+$', line_before_cursor)
                if match:
                    word_before_cursor = match.group(0)
                
                # If we have a word that could be a snippet prefix
                if word_before_cursor:
                    # Get standard snippets
                    import snippets
                    snippet_manager = snippets.get_snippet_manager()
                    matching_snippets = snippet_manager.get_matching_snippets(language, word_before_cursor)
                    
                    # Get AI-generated snippets
                    import ai_snippets
                    ai_snippet_generator = ai_snippets.get_ai_snippet_generator()
                    ai_matching_snippets = ai_snippet_generator.get_matching_snippets(language, word_before_cursor)
                    
                    # Add AI snippets to completions if any match
                    if ai_matching_snippets:
                        # Prepend AI-generated snippets to show them first
                        matching_snippets = ai_matching_snippets + matching_snippets
                    
                    # Add snippets to completions
                    if matching_snippets:
                        # Include AI snippets in completions
                        for snippet in matching_snippets:
                            # Add snippet objects directly
                            completions.append(snippet)
        
        # Set completion state
        self.completion.completions = completions
        self.completion.position = position
        self.completion.current_index = 0
        self.completion.trigger_position = position[1]  # Column where triggered
        
        # Animate appearance
        import micro_animations
        self.completion.opacity = 0.0  # Start invisible
        self.completion.scale = 0.95   # Start slightly smaller
        self.completion.visible = True
        self.completion.animating = True
        self.completion.animation_direction = "in"
        
        # Start animation
        micro_animations.get_micro_animations().animate_code_completion_popup(
            self.completion, appearing=True
        )
        
    def hide_code_completion(self):
        """Hide the code completion popup with animation"""
        if not self.completion.visible:
            return
            
        # Animate disappearance
        import micro_animations
        self.completion.animating = True
        self.completion.animation_direction = "out"
        
        # Start animation
        micro_animations.get_micro_animations().animate_code_completion_popup(
            self.completion, appearing=False
        )
        
        # Flag as hidden - animations will fade it out
        self.completion.visible = False
        
    def select_next_completion(self):
        """Select the next completion in the list"""
        if not self.completion.visible or not self.completion.completions:
            return
            
        # Move to next item, wrapping around
        self.completion.current_index = (self.completion.current_index + 1) % len(self.completion.completions)
        
        # Animate selection
        import micro_animations
        micro_animations.get_micro_animations().animate_completion_selection(self.completion)
        
    def select_prev_completion(self):
        """Select the previous completion in the list"""
        if not self.completion.visible or not self.completion.completions:
            return
            
        # Move to previous item, wrapping around
        self.completion.current_index = (self.completion.current_index - 1) % len(self.completion.completions)
        
        # Animate selection
        import micro_animations
        micro_animations.get_micro_animations().animate_completion_selection(self.completion)
        
    def accept_selected_completion(self):
        """Accept the currently selected completion"""
        if not self.completion.visible or not self.completion.completions:
            return None
            
        # Get the selected completion
        selected = self.completion.completions[self.completion.current_index]
        
        # Check if the selected completion is a snippet
        active_tab = self.get_active_tab()
        
        # Handle snippets differently than regular completions
        if isinstance(selected, snippets.Snippet):
            # Get the buffer for the current tab
            buffer = active_tab.buffer if active_tab else None
            if buffer:
                # Get cursor position
                cursor_position = buffer.cursor_position
                
                # Get the text from the document
                document = buffer.document
                text = document.text
                
                # Calculate the position where to insert the snippet
                # (Remove the trigger text that's already in the document)
                trigger_text = selected.prefix
                trigger_pos = cursor_position - len(trigger_text)
                
                if trigger_pos >= 0 and text[trigger_pos:cursor_position] == trigger_text:
                    # Get the snippet expanded text and placeholder positions
                    insertion_text, placeholder_positions = selected.get_insertion_text()
                    
                    # Replace the trigger text with the expanded snippet
                    new_text = text[:trigger_pos] + insertion_text + text[cursor_position:]
                    buffer.text = new_text
                    
                    # Set new cursor position to the first placeholder or end of insertion
                    if placeholder_positions:
                        # Store placeholder information for navigation
                        self.completion.is_snippet = True
                        self.completion.active_snippet = selected
                        self.completion.snippet_placeholders = placeholder_positions
                        self.completion.current_placeholder = 0
                        
                        # Move cursor to the first placeholder
                        first_placeholder = placeholder_positions[0]
                        new_cursor_pos = trigger_pos + first_placeholder[0]
                        buffer.cursor_position = new_cursor_pos
                        
                        # Select the placeholder text
                        buffer.selection_state = SelectionState(
                            original_cursor_position=new_cursor_pos,
                            cursor_position=trigger_pos + first_placeholder[1]
                        )
                        
                        # Show status message about navigating placeholders
                        self.status_message = f"Snippet '{selected.name}' inserted. Tab to navigate placeholders."
                        self.status_type = "info"
                    else:
                        # No placeholders, set cursor to end of insertion
                        buffer.cursor_position = trigger_pos + len(insertion_text)
                        self.status_message = f"Snippet '{selected.name}' inserted."
                        self.status_type = "info"
            
            # Hide the completion popup
            self.hide_code_completion()
            
            return selected.name  # Return snippet name for status message
        else:
            # Regular completion (just text)
            # Hide the completion popup
            self.hide_code_completion()
            
            return selected
            
    def navigate_next_snippet_placeholder(self):
        """Navigate to the next placeholder in the active snippet"""
        if not self.completion.is_snippet or not self.completion.snippet_placeholders:
            return False
            
        active_tab = self.get_active_tab()
        if not active_tab or not active_tab.buffer:
            return False
            
        # If we're at the last placeholder, cancel snippet mode
        if self.completion.current_placeholder >= len(self.completion.snippet_placeholders) - 1:
            self.completion.is_snippet = False
            self.completion.active_snippet = None
            self.completion.snippet_placeholders = []
            self.completion.current_placeholder = 0
            
            # Remove selection and show status message
            active_tab.buffer.selection_state = None
            self.status_message = "Snippet editing completed."
            self.status_type = "info"
            return True
            
        # Move to the next placeholder
        self.completion.current_placeholder += 1
        
        # Get the new placeholder position
        buffer = active_tab.buffer
        document = buffer.document
        text = document.text
        
        # Get the placeholder start and end positions
        placeholder = self.completion.snippet_placeholders[self.completion.current_placeholder]
        placeholder_start, placeholder_end, placeholder_text = placeholder
        
        # Move cursor to the placeholder start and select the text
        buffer.cursor_position = placeholder_start
        buffer.selection_state = SelectionState(
            original_cursor_position=placeholder_start,
            cursor_position=placeholder_end
        )
        
        # Show status message
        self.status_message = f"Placeholder {self.completion.current_placeholder+1}/{len(self.completion.snippet_placeholders)}"
        self.status_type = "info"
        
        return True
        
    def navigate_prev_snippet_placeholder(self):
        """Navigate to the previous placeholder in the active snippet"""
        if not self.completion.is_snippet or not self.completion.snippet_placeholders:
            return False
            
        active_tab = self.get_active_tab()
        if not active_tab or not active_tab.buffer:
            return False
            
        # If we're at the first placeholder, stay there
        if self.completion.current_placeholder <= 0:
            self.status_message = "Already at first placeholder."
            self.status_type = "info"
            return True
            
        # Move to the previous placeholder
        self.completion.current_placeholder -= 1
        
        # Get the new placeholder position
        buffer = active_tab.buffer
        document = buffer.document
        text = document.text
        
        # Get the placeholder start and end positions
        placeholder = self.completion.snippet_placeholders[self.completion.current_placeholder]
        placeholder_start, placeholder_end, placeholder_text = placeholder
        
        # Move cursor to the placeholder start and select the text
        buffer.cursor_position = placeholder_start
        buffer.selection_state = SelectionState(
            original_cursor_position=placeholder_start,
            cursor_position=placeholder_end
        )
        
        # Show status message
        self.status_message = f"Placeholder {self.completion.current_placeholder+1}/{len(self.completion.snippet_placeholders)}"
        self.status_type = "info"
        
        return True
        
    def set_theme(self, theme_name):
        """Set the editor theme
        
        Args:
            theme_name (str): Name of the theme to use
            
        Returns:
            bool: True if theme was set successfully, False otherwise
        """
        from themes import get_available_themes
        available_themes = get_available_themes()
        
        if theme_name in available_themes:
            # Store the old theme for transition effects
            old_theme = self.current_theme
            
            # Set the new theme
            self.current_theme = theme_name
            self.status_message = f"Theme changed to {theme_name}"
            self.status_type = "info"
            
            # Apply theme transition animation if animations are enabled
            if self.enable_animations:
                # Create a property to track theme transition
                if not hasattr(self, 'theme_transition_progress'):
                    self.theme_transition_progress = 0.0
                
                # Define the theme transition animation
                class ThemeTransitionAnimation(animations.AnimationState):
                    def __init__(self, target, old_theme, new_theme):
                        super().__init__()
                        self.target = target
                        self.old_theme = old_theme
                        self.new_theme = new_theme
                        self.duration = 0.4  # Medium duration for smooth transition
                        
                    def on_frame(self):
                        # Update transition progress
                        progress = self.get_eased_progress("ease_out_cubic")
                        self.target.theme_transition_progress = progress
                        refresh_editor_view()
                
                # Start the transition animation
                transition = ThemeTransitionAnimation(self, old_theme, theme_name)
                animations.animation_manager.add_animation("theme_transition", transition)
                animations.animation_manager.start_animation("theme_transition")
                
            return True
        else:
            self.status_message = f"Theme '{theme_name}' not found"
            self.status_type = "error"
            return False
            
    def cycle_theme(self):
        """Cycle to the next available theme
        
        Returns:
            str: Name of the new theme
        """
        from themes import get_available_themes
        available_themes = get_available_themes()
        
        # Find current theme index
        try:
            current_index = available_themes.index(self.current_theme)
            # Move to the next theme (wrap around if at the end)
            next_index = (current_index + 1) % len(available_themes)
            next_theme = available_themes[next_index]
        except (ValueError, IndexError):
            # If current theme not found or themes list empty, use first theme
            next_theme = available_themes[0] if available_themes else "default"
            
        # Set the new theme
        self.set_theme(next_theme)
        return next_theme
        
    def toggle_fold_at_cursor(self):
        """Toggle folding for the block at the current cursor position"""
        active_tab = self.get_active_tab()
        if not active_tab or not active_tab.buffer or not self.folding_enabled:
            return False
            
        if not active_tab.filename in self.folded_regions:
            self.folded_regions[active_tab.filename] = []
            
        # Get the current line number (0-indexed)
        cursor_line = active_tab.buffer.document.cursor_position_row
        
        # Find the fold region at this position (if any)
        fold_region = self._find_fold_region(active_tab.buffer.text, cursor_line)
        if not fold_region:
            return False
            
        start_line, end_line = fold_region
        
        # Check if this region is already folded
        is_unfolding = False
        for existing_start, existing_end in self.folded_regions[active_tab.filename]:
            if existing_start == start_line:
                # Already folded, unfold it
                is_unfolding = True
                self.folded_regions[active_tab.filename].remove((existing_start, existing_end))
                self.status_message = f"Unfolded lines {start_line+1}-{end_line+1}"
                self.status_type = "info"
                
                # Apply micro-animation for unfolding if enabled
                if self.enable_animations:
                    import micro_animations
                    
                    # Create an animation target object for this fold
                    fold_id = f"fold_{active_tab.filename}_{start_line}"
                    if fold_id not in self.button_states:
                        self.button_states[fold_id] = type('FoldState', (), {'highlight': 0.0})
                        
                    # Micro-animation for unfolding (brief flash)
                    micro_animations.get_micro_animations().animate_button_press(
                        self.button_states[fold_id]
                    )
                
                return True
                
        # Not folded, fold it
        self.folded_regions[active_tab.filename].append((start_line, end_line))
        self.status_message = f"Folded lines {start_line+1}-{end_line+1}"
        self.status_type = "info"
        
        # Apply micro-animation for folding if enabled
        if self.enable_animations:
            import micro_animations
            
            # Create an animation target object for this fold
            fold_id = f"fold_{active_tab.filename}_{start_line}"
            if fold_id not in self.button_states:
                self.button_states[fold_id] = type('FoldState', (), {'highlight': 0.0})
                
            # Use a slightly different animation for folding vs unfolding
            class FoldAnimation(animations.AnimationState):
                def __init__(self, target):
                    super().__init__()
                    self.target = target
                    self.duration = 0.3
                    
                def on_frame(self):
                    progress = self.get_eased_progress("ease_out_quad")
                    self.target.highlight = progress
                    refresh_editor_view()
            
            # Start the fold animation
            fold_anim = FoldAnimation(self.button_states[fold_id])
            animations.animation_manager.add_animation(fold_id, fold_anim)
            animations.animation_manager.start_animation(fold_id)
            
        return True
    
    def _find_fold_region(self, text, cursor_line):
        """Find a foldable region that includes the cursor line"""
        lines = text.split('\n')
        if cursor_line >= len(lines):
            return None
            
        # Check if this line starts a block that can be folded
        current_line = lines[cursor_line].rstrip()
        
        # Python-specific: look for lines ending with a colon (function/class/loop/if definitions)
        if current_line.endswith(':'):
            # Find the indentation level of this line
            current_indent = len(current_line) - len(current_line.lstrip())
            
            # Find where this block ends
            end_line = cursor_line
            for i in range(cursor_line + 1, len(lines)):
                line = lines[i].rstrip()
                if not line:  # Skip empty lines
                    continue
                    
                # If we find a line with the same or less indentation, 
                # that's the end of our block
                indent = len(line) - len(line.lstrip())
                if indent <= current_indent:
                    end_line = i - 1
                    break
                end_line = i
                
            # If we found a valid region, return it
            if end_line > cursor_line:
                return (cursor_line, end_line)
                
        return None
        
    def toggle_search_ui(self):
        """Toggle search interface visibility"""
        # Toggle the state
        self.show_search_ui = not self.show_search_ui
        
        # Import micro_animations here to avoid circular imports
        if self.enable_animations:
            import micro_animations
            
            # Create a toggle state object if it doesn't exist
            toggle_id = "search_panel"
            if toggle_id not in self.toggle_states:
                self.toggle_states[toggle_id] = type('ToggleState', (), {'highlight': 0.0})
                
            # Animate the toggle effect
            micro_animations.get_micro_animations().animate_toggle(
                self.toggle_states[toggle_id], 
                self.show_search_ui
            )
            
            # Animate panel appearance/disappearance
            if self.show_search_ui:
                # Start at 0 and animate to 1
                self.search_panel_opacity = 0.0
                
                # Create and start a fade-in animation
                class PanelFadeIn(animations.AnimationState):
                    def __init__(self, target):
                        super().__init__()
                        self.target = target
                        self.duration = 0.2  # Quick animation
                        
                    def on_frame(self):
                        progress = self.get_eased_progress("ease_out_cubic")
                        self.target.search_panel_opacity = progress
                        refresh_editor_view()
                
                fade_in = PanelFadeIn(self)
                animations.animation_manager.add_animation("search_panel_fade", fade_in)
                animations.animation_manager.start_animation("search_panel_fade")
            else:
                # Fade out animation
                self.search_panel_opacity = 1.0
                
                class PanelFadeOut(animations.AnimationState):
                    def __init__(self, target):
                        super().__init__()
                        self.target = target
                        self.duration = 0.15  # Faster fade out
                        
                    def on_frame(self):
                        progress = self.get_eased_progress("ease_in_cubic")
                        self.target.search_panel_opacity = 1.0 - progress
                        refresh_editor_view()
                    
                    def on_complete(self):
                        # Clear search state when hiding search UI and animation is finished
                        self.target.search_query = ""
                        self.target.search_results = []
                        self.target.current_search_index = 0
                
                fade_out = PanelFadeOut(self)
                animations.animation_manager.add_animation("search_panel_fade_out", fade_out)
                animations.animation_manager.start_animation("search_panel_fade_out")
        else:
            # No animations - clear search state immediately when hiding
            if not self.show_search_ui:
                self.search_query = ""
                self.search_results = []
                self.current_search_index = 0
                
        return self.show_search_ui
        
    def perform_search(self, query, case_sensitive=False):
        """Perform a search in the current buffer"""
        active_tab = self.get_active_tab()
        if not active_tab or not query:
            return []
            
        text = active_tab.buffer.text
        if not text:
            return []
            
        # Reset search state
        self.search_results = []
        self.current_search_index = 0
        self.search_query = query
        
        # Perform the search
        if not case_sensitive:
            query = query.lower()
            text_to_search = text.lower()
        else:
            text_to_search = text
            
        start_pos = 0
        while True:
            pos = text_to_search.find(query, start_pos)
            if pos == -1:
                break
                
            self.search_results.append((pos, pos + len(query)))
            start_pos = pos + 1
            
        return self.search_results
        
    def goto_next_search_result(self):
        """Move to the next search result"""
        if not self.search_results:
            return None
            
        # Get the previous index for animations
        prev_index = self.current_search_index
            
        # Increment the index and wrap around if needed
        if self.current_search_index < len(self.search_results) - 1:
            self.current_search_index += 1
        else:
            self.current_search_index = 0
            
        # Apply animations if enabled
        if self.enable_animations:
            self._animate_search_navigation(prev_index, self.current_search_index)
            
        # Return the current result for cursor positioning
        return self.search_results[self.current_search_index]
        
    def goto_prev_search_result(self):
        """Move to the previous search result"""
        if not self.search_results:
            return None
            
        # Get the previous index for animations
        prev_index = self.current_search_index
            
        # Decrement the index and wrap around if needed
        if self.current_search_index > 0:
            self.current_search_index -= 1
        else:
            self.current_search_index = len(self.search_results) - 1
            
        # Apply animations if enabled
        if self.enable_animations:
            self._animate_search_navigation(prev_index, self.current_search_index)
            
        # Return the current result for cursor positioning
        return self.search_results[self.current_search_index]
        
    def _animate_search_navigation(self, prev_index, new_index):
        """Apply animations when navigating between search results
        
        Args:
            prev_index: The previous search result index
            new_index: The new search result index
        """
        import micro_animations
        
        # Create animation target objects if they don't exist
        if not hasattr(self, 'search_result_states'):
            self.search_result_states = {}
            
        # Create or update state objects for all results
        for i, (start, end) in enumerate(self.search_results):
            result_id = f"search_result_{i}"
            if result_id not in self.search_result_states:
                self.search_result_states[result_id] = type('SearchResultState', (), {
                    'highlight_intensity': 0.5,
                    'scale': 1.0
                })
                
            # Animate the current and previous results
            if i == new_index:
                # Current result - apply a navigation animation
                micro_animations.get_micro_animations().animate_search_navigation(
                    self.search_result_states[result_id]
                )
            elif i == prev_index:
                # Previous result - remove its current status
                micro_animations.get_micro_animations().animate_search_result(
                    self.search_result_states[result_id],
                    is_current=False
                )
            elif i not in (prev_index, new_index):
                # Other results - make sure they have the basic animation
                micro_animations.get_micro_animations().animate_search_result(
                    self.search_result_states[result_id],
                    is_current=False
                )
        
    def replace_current_match(self, replace_text):
        """Replace the current search match with the specified text"""
        if not self.search_results or self.current_search_index >= len(self.search_results):
            return False
            
        active_tab = self.get_active_tab()
        if not active_tab:
            return False
            
        # Get the current match position
        start, end = self.search_results[self.current_search_index]
        
        # Replace the text in the buffer
        buffer = active_tab.buffer
        text = buffer.text
        new_text = text[:start] + replace_text + text[end:]
        
        # Update the buffer
        cursor_position = start + len(replace_text)
        buffer.document = Document(new_text, cursor_position)
        active_tab.modified = True
        
        # Update the search results to account for the replaced text
        length_diff = len(replace_text) - (end - start)
        
        # Update positions of all subsequent matches
        for i in range(self.current_search_index + 1, len(self.search_results)):
            match_start, match_end = self.search_results[i]
            self.search_results[i] = (match_start + length_diff, match_end + length_diff)
            
        # Remove the current match from results
        self.search_results.pop(self.current_search_index)
        
        # Adjust current index if needed
        if self.search_results and self.current_search_index >= len(self.search_results):
            self.current_search_index = 0
            
        return True
        
    def replace_all_matches(self, replace_text):
        """Replace all search matches with the specified text"""
        if not self.search_results:
            return 0
            
        active_tab = self.get_active_tab()
        if not active_tab:
            return 0
            
        # Get the buffer text
        buffer = active_tab.buffer
        text = buffer.text
        
        # Sort results in reverse order to avoid invalidating positions
        sorted_results = sorted(self.search_results, reverse=True)
        
        # Perform replacements
        for start, end in sorted_results:
            text = text[:start] + replace_text + text[end:]
            
        # Update the buffer
        buffer.document = Document(text, 0)
        active_tab.modified = True
        
        # Clear search results since they're no longer valid
        replaced_count = len(self.search_results)
        self.search_results = []
        self.current_search_index = 0
        
        return replaced_count
    
    def request_code_insight(self):
        """Request AI-powered insight for the current code context"""
        active_tab = self.get_active_tab()
        if not active_tab:
            self.status_message = "No active tab to analyze"
            self.status_type = "warning"
            return False
        
        # Get current buffer text and cursor position
        buffer = active_tab.buffer
        text = buffer.text
        if not text.strip():
            self.status_message = "Empty buffer, nothing to analyze"
            self.status_type = "warning"
            return False
        
        # Get current line number (0-indexed)
        line_number = buffer.document.cursor_position_row
        
        # Set analyzing flag
        self.analyzing_code = True
        self.status_message = "Analyzing code..."
        self.status_type = "info"
        
        # Start a thread to check for analysis results
        def check_for_results():
            while self.analyzing_code:
                insight = ai_context.get_latest_insight()
                if insight:
                    self.current_insight = insight
                    self.analyzing_code = False
                    self.status_message = "Code analysis complete"
                    self.status_type = "info"
                    break
                time.sleep(0.1)
        
        # Start the checking thread
        threading.Thread(target=check_for_results, daemon=True).start()
        
        # Request analysis in the background
        ai_context.request_analysis(text, line_number, active_tab.filename)
        return True
    
    @property
    def current_file(self):
        """Get the current file (for backwards compatibility)"""
        tab = self.get_active_tab()
        return tab.filename if tab else None
    
    @current_file.setter
    def current_file(self, value):
        """Set the current file (for backwards compatibility)"""
        tab = self.get_active_tab()
        if tab:
            tab.filename = value
    
    @property
    def modified(self):
        """Get modified state (for backwards compatibility)"""
        tab = self.get_active_tab()
        return tab.modified if tab else False
    
    @modified.setter
    def modified(self, value):
        """Set modified state (for backwards compatibility)"""
        tab = self.get_active_tab()
        if tab:
            tab.modified = value

# Initialize global state
editor_state = EditorState()

def get_lexer_for_file(filename):
    """Get the appropriate lexer for syntax highlighting based on file extension"""
    from pygments.styles import get_style_by_name
    from pygments import highlight
    from pygments.formatters import Terminal256Formatter
    
    # Get the current theme name from the editor state
    current_theme = getattr(editor_state, 'current_theme', 'dracula')
    
    if filename:
        try:
            # Determine the language for this file
            language = syntax_styles.get_language_from_filename(filename)
            
            # Get a lexer for this file type
            lexer = get_lexer_for_filename(filename, stripnl=False)
            
            # Get enhanced syntax styles for this language
            syntax_style = syntax_styles.get_syntax_styles(language, current_theme)
            
            # Create a PygmentsLexer with custom styles
            return PygmentsLexer(lexer.__class__, style_dict=syntax_style)
        except ClassNotFound:
            # Create an instance of TextLexer class with default styles
            return PygmentsLexer(TextLexer)
        except Exception as e:
            # Fallback in case of any error
            print(f"Error creating lexer: {e}")
            return PygmentsLexer(TextLexer)
    
    # Use TextLexer class for unknown files
    return PygmentsLexer(TextLexer)

def load_file(filename, buffer):
    """Load a file into the buffer"""
    if not filename:
        return False
    
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            buffer.document = Document(content, 0)
            editor_state.current_file = filename
            editor_state.modified = False
            editor_state.status_message = f"Loaded file: {filename}"
            editor_state.status_type = "info"
            return True
        else:
            editor_state.current_file = filename
            editor_state.status_message = f"New file: {filename}"
            editor_state.status_type = "info"
            return True
    except Exception as e:
        editor_state.status_message = f"Error loading file: {str(e)}"
        editor_state.status_type = "error"
        return False

def save_file(buffer, silent=False):
    """Save buffer contents to a file
    
    Args:
        buffer: The buffer to save
        silent: If True, don't update status messages (for auto-save)
    """
    active_tab = editor_state.get_active_tab()
    if not active_tab or not active_tab.filename:
        if not silent:
            editor_state.status_message = "No file name specified"
            editor_state.status_type = "error"
        return False
    
    try:
        with open(active_tab.filename, 'w', encoding='utf-8') as f:
            f.write(buffer.text)
        active_tab.modified = False
        
        # Update last save time for auto-save tracking
        editor_state.last_save_time[active_tab.filename] = time.time()
        
        # Run syntax check if enabled
        if editor_state.syntax_check_enabled and editor_state.check_on_save:
            editor_state.check_current_file_syntax()
        
        if not silent:
            editor_state.status_message = f"Saved to {active_tab.filename}"
            editor_state.status_type = "info"
        return True
    except Exception as e:
        if not silent:
            editor_state.status_message = f"Error saving file: {str(e)}"
            editor_state.status_type = "error"
        return False

def check_auto_save():
    """Check if files need to be auto-saved based on time interval"""
    if not editor_state.auto_save_enabled:
        return
        
    current_time = time.time()
    
    for tab in editor_state.tabs:
        if not tab.modified or not tab.filename:
            continue
            
        # Check if it's time to auto-save this file
        last_save = editor_state.last_save_time.get(tab.filename, 0)
        if current_time - last_save >= editor_state.auto_save_interval:
            save_file(tab.buffer, silent=True)
            
            # Show brief status message
            editor_state.status_message = f"Auto-saved {os.path.basename(tab.filename)}"
            editor_state.status_type = "info"

def create_editor_buffer(filename=None):
    """Create the main editor buffer with auto-indentation support"""
    # Create key bindings for the buffer
    kb = KeyBindings()
    
    # Add auto-indentation on Enter key
    @kb.add('enter')
    def _(event):
        """Apply auto-indentation when Enter is pressed"""
        return auto_indent.apply_auto_indent(event.current_buffer, event)
    
    # Create buffer with custom key bindings
    buffer = Buffer(key_bindings=kb)
    
    if filename:
        load_file(filename, buffer)
    
    return buffer

def create_status_bar_text():
    """Create formatted text for the status bar"""
    # Get active tab
    active_tab = editor_state.get_active_tab()
    
    # Get file name display
    if active_tab and active_tab.filename:
        file_display = active_tab.filename
    else:
        file_display = "[No File]"
        
    # Add modified marker if needed
    if active_tab and active_tab.modified:
        file_display += " [+]"
    
    # Add tab position information
    if editor_state.tabs:
        tab_info = f" [{editor_state.active_tab_index + 1}/{len(editor_state.tabs)}]"
    else:
        tab_info = ""
    
    # Create status bar components
    mode_text = [("class:status-bar.mode", f" {editor_state.editor_mode} ")]
    file_text = [("class:status-bar.filename", f" {file_display}{tab_info} ")]
    
    # Syntax checking indicator
    syntax_text = []
    if editor_state.syntax_check_enabled:
        if active_tab and active_tab.filename in editor_state.syntax_errors:
            error_count = len(editor_state.syntax_errors[active_tab.filename])
            if error_count > 0:
                syntax_text = [("class:status-bar.error", f" Syntax: {error_count} issues ")]
            else:
                syntax_text = [("class:status-bar.info", " Syntax: OK ")]
        else:
            syntax_text = [("class:status-bar.info", " Syntax: -- ")]
    
    # Status message with appropriate style
    message_class = f"class:status-bar.{editor_state.status_type}"
    message_text = [(message_class, f" {editor_state.status_message} ")]
    
    # Combine all parts with appropriate spacing
    return mode_text + file_text + syntax_text + [("class:status-bar", " " * 3)] + message_text

# Tab animation state
# Import animation framework
import animations

class TabAnimationState:
    """Tracks tab animation state"""
    def __init__(self):
        self.animating = False
        self.from_index = 0
        self.to_index = 0
        self.step = 0
        self.max_steps = 5  # Number of animation frames
        self.animation_start_time = 0
        self.progress = 0.0  # Animation progress from 0.0 to 1.0

# Add to editor_state
editor_state.tab_animation = TabAnimationState()

class TabTransitionAnimation(animations.AnimationState):
    """Enhanced tab transition animation"""
    def __init__(self, from_index, to_index):
        super().__init__()
        self.from_index = from_index
        self.to_index = to_index
        self.max_steps = 8  # More animation frames for smoother transition
        self.duration = 0.2  # Slightly faster animation
        
    def on_frame(self):
        """Update the tab animation state on each frame"""
        # Use eased progress for smoother animation
        progress = self.get_eased_progress("ease_out_quad")
        
        # Update tab animation state
        editor_state.tab_animation.animating = True
        editor_state.tab_animation.from_index = self.from_index
        editor_state.tab_animation.to_index = self.to_index
        editor_state.tab_animation.step = self.current_step
        editor_state.tab_animation.progress = progress
        
        # Ensure UI is refreshed
        if editor_app:
            editor_app.invalidate()
            
    def on_complete(self):
        """Called when the animation completes"""
        super().on_complete()
        
        # Clean up the animation state
        editor_state.tab_animation.animating = False
        editor_state.tab_animation.progress = 1.0
        
        # Ensure UI is refreshed one last time
        if editor_app:
            editor_app.invalidate()

def animate_tab_transition(from_index, to_index):
    """Start tab transition animation"""
    if from_index == to_index:
        return
        
    # Only animate if enabled in preferences
    if not getattr(editor_state, 'enable_animations', True):
        return
        
    # Create and start a new tab transition animation
    animation = TabTransitionAnimation(from_index, to_index)
    animations.animation_manager.add_animation('tab_transition', animation)
    animation.start()

# We no longer need TabAnimationProcessor as its functionality is incorporated directly into get_tab_text
# Kept here as comment for reference
# class TabAnimationProcessor(Processor):
#     """Processor that animates tab transitions"""
#     
#     def apply_transformation(self, transformation_input):
#         """Apply animation transformation to the tabs"""
#         if not editor_state.tab_animation.animating:
#             return Transformation(transformation_input.fragments)
#             
#         # Create a new list of fragments with animation effects
#         new_fragments = []
#         
#         for fragment in transformation_input.fragments:
#             # Apply animation effect based on progress
#             progress = editor_state.tab_animation.step / editor_state.tab_animation.max_steps
#             
#             # Determine if this fragment needs animation
#             if "class:tab.active" in fragment.style:
#                 # Add a slight fade-in effect for the active tab
#                 alpha = min(1.0, progress * 2)
#                 # Add highlight color based on animation stage
#                 highlight = f" bg:#3465a4{int(alpha * 70):02x}"
#                 new_fragments.append(Fragment(fragment.text, fragment.style + highlight))
#             else:
#                 new_fragments.append(fragment)
#         
#         return Transformation(new_fragments)

def create_tab_bar():
    """Create the tab bar display"""
    def get_tab_text():
        result = []
        for index, tab in enumerate(editor_state.tabs):
            # Determine file name for display
            name = tab.filename if tab.filename else "[No File]"
            name = os.path.basename(name)  # Just get the filename part
            
            # Mark modified tabs with an asterisk
            if tab.modified:
                name += "*"
            
            # Animation transitions
            animation = editor_state.tab_animation
            is_animating = animation.animating and (index == animation.from_index or index == animation.to_index)
            
            # Apply animation effects directly to the tabs
            base_style = None
            
            # Style differently if it's the active tab
            if index == editor_state.active_tab_index:
                # Use slightly different style during animation
                if is_animating and index == animation.to_index:
                    # Calculate transition progress (0.0 to 1.0)
                    progress = animation.progress
                    # Add an arrow indicator during animation
                    arrow = "→ " if animation.from_index < animation.to_index else "← "
                    
                    # Apply animation effects for the active tab
                    base_style = "class:tab.active"
                    # Add highlight color based on animation progress
                    alpha = min(1.0, progress * 2)
                    highlight = f" bg:#3465a4{int(alpha * 70):02x}"
                    style = base_style + highlight
                    
                    result.append((style, f" {index+1}: {arrow}{name} "))
                else:
                    result.append(("class:tab.active", f" {index+1}: {name} "))
            else:
                # Use slightly different style during animation
                if is_animating and index == animation.from_index:
                    # Calculate transition progress (0.0 to 1.0)
                    progress = animation.progress
                    result.append(("class:tab.transitioning", f" {index+1}: {name} "))
                else:
                    result.append(("class:tab", f" {index+1}: {name} "))
        
        # Add a placeholder for new tab button
        result.append(("class:tab.new", " + "))
        
        return result
    
    return Window(
        content=FormattedTextControl(
            get_tab_text,
        ),
        height=1,
        style="class:tab-bar",
    )

def get_active_editor_window():
    """Get the editor window for the active tab"""
    active_tab = editor_state.get_active_tab()
    if not active_tab:
        # Create at least one tab if none exists
        active_tab = editor_state.add_tab()
        # Initialize the tab properly
        active_tab.lexer = get_lexer_for_file(active_tab.filename)
    
    # Ensure the buffer exists - it should always be created in EditorTab.__init__
    if not active_tab.buffer:
        active_tab.buffer = Buffer()
        
    # Ensure lexer is initialized
    if not active_tab.lexer:
        active_tab.lexer = get_lexer_for_file(active_tab.filename)
    
    # Use the editor state for line wrapping and line numbers
    left_margins = [NumberedMargin()] if editor_state.line_numbers else []
    
    # Create custom processors
    processors = [HighlightMatchingBracketProcessor()]
    
    # Add search result highlighting processor
    if editor_state.search_results and editor_state.show_search_ui:
        processors.append(SearchResultProcessor())
    
    # Add syntax error processor if enabled
    # First check if syntax_errors exists and if filename exists
    if (editor_state.syntax_check_enabled and active_tab.filename and 
        active_tab.filename in editor_state.syntax_errors):
        processors.append(SyntaxErrorProcessor(active_tab.filename))
    
    # Add code folding processor if enabled
    # First check if folded_regions exists and if filename exists
    if (editor_state.folding_enabled and active_tab.filename and 
        active_tab.filename in editor_state.folded_regions):
        processors.append(FoldingProcessor(active_tab.filename))
    
    # Add insight tooltip processor if enabled
    if hasattr(editor_state, 'tooltips') and editor_state.tooltips.show_tooltips:
        processors.append(InsightTooltipProcessor())
        
    # Add code completion popup processor
    if hasattr(editor_state, 'completion'):
        processors.append(CompletionProcessor())
    
    return Window(
        BufferControl(
            buffer=active_tab.buffer,
            lexer=active_tab.lexer,
            include_default_input_processors=True,
            input_processors=processors,
        ),
        left_margins=left_margins,
        cursorline=True,
        wrap_lines=editor_state.wrap_lines,
    )

class SearchResultProcessor(Processor):
    """Processor that highlights search results in the text"""
    
    def apply_transformation(self, transformation_input):
        """Apply transformation to highlight search results"""
        buffer_control = transformation_input.buffer_control
        document = transformation_input.document
        lineno = transformation_input.lineno
        line_text = document.lines[lineno]
        
        # Get search results information from the editor state
        if not editor_state.search_results or not editor_state.show_search_ui:
            return Transformation(transformation_input.fragments)
        
        # Find all search results on this line
        line_start_pos = document.translate_row_col_to_index(lineno, 0)
        line_end_pos = line_start_pos + len(line_text)
        
        # Get search results that overlap with this line
        line_results = []
        for i, (start, end) in enumerate(editor_state.search_results):
            if end > line_start_pos and start < line_end_pos:
                # Translate to line-relative positions
                rel_start = max(0, start - line_start_pos)
                rel_end = min(len(line_text), end - line_start_pos)
                line_results.append((i, rel_start, rel_end))
        
        if not line_results:
            return Transformation(transformation_input.fragments)
        
        # Create new fragments with search result highlighting
        result_fragments = []
        current_pos = 0
        
        # Get animation states for styling
        if hasattr(editor_state, 'search_result_states'):
            search_states = editor_state.search_result_states
        else:
            search_states = {}
        
        # Create fragments by splitting the line at each search result boundary
        for i, start, end in sorted(line_results, key=lambda x: x[1]):
            # Add text before the search result
            if start > current_pos:
                for fragment, text in transformation_input.fragments:
                    frag_start = current_pos
                    frag_end = current_pos + len(text)
                    
                    # Only include the part before the search result
                    if frag_end <= start:
                        result_fragments.append((fragment, text))
                        current_pos = frag_end
                    else:
                        overlap = min(frag_end, start) - frag_start
                        if overlap > 0:
                            result_fragments.append((fragment, text[:overlap]))
                        current_pos += overlap
            
            # Add the search result with highlight styling
            if end > current_pos:
                result_text = line_text[current_pos:end]
                
                # Determine highlight intensity based on animation state
                is_current = (i == editor_state.current_search_index)
                highlight_style = "class:search-result"
                
                # Apply animation state if available
                result_id = f"search_result_{i}"
                if result_id in search_states:
                    state = search_states[result_id]
                    
                    # Add intensity to highlight based on animation state
                    if hasattr(state, "highlight_intensity"):
                        intensity = state.highlight_intensity
                        if is_current:
                            highlight_style = f"class:search-result.current"
                    
                    # Apply scale if set (not actually visible but good to track)
                    if hasattr(state, "scale") and state.scale != 1.0:
                        # Could apply additional styling for the "pop" effect
                        pass
                        
                elif is_current:
                    highlight_style = f"class:search-result.current"
                
                result_fragments.append((highlight_style, result_text))
                current_pos = end
        
        # Add remaining text after the last search result
        if current_pos < len(line_text):
            for fragment, text in transformation_input.fragments:
                frag_start = current_pos
                frag_end = current_pos + len(text)
                
                # Only include the part after the last search result
                if frag_start >= current_pos:
                    remaining_text = text[max(0, current_pos - frag_start):]
                    if remaining_text:
                        result_fragments.append((fragment, remaining_text))
                    current_pos = frag_end
        
        return Transformation(result_fragments)

class SyntaxErrorProcessor(Processor):
    """Processor that highlights syntax errors in the code"""
    
    def __init__(self, filename):
        self.filename = filename
        
    def apply_transformation(self, transformation_input):
        """Apply transformation to highlight syntax errors"""
        document = transformation_input.document
        syntax_errors = editor_state.syntax_errors.get(self.filename, [])
        
        # No syntax errors to highlight
        if not syntax_errors:
            return Transformation(transformation_input.fragments)
        
        # Create a map of line numbers to errors
        line_to_errors = {}
        for error in syntax_errors:
            line = error.line_number - 1  # Convert to 0-based
            if line not in line_to_errors:
                line_to_errors[line] = []
            line_to_errors[line].append(error)
        
        # Create a new list of fragments with error highlighting
        new_fragments = []
        
        for fragment in transformation_input.fragments:
            line = get_fragment_line(fragment, transformation_input)
            
            # Check if this line has errors
            if line in line_to_errors:
                errors = line_to_errors[line]
                
                # If we have column information and this is a syntax error (not style)
                if any(error.error_type == "syntax" and error.column > 0 for error in errors):
                    # We'll try to highlight just the problematic part
                    text = fragment.text
                    current_pos = 0
                    
                    # Collect parts with proper styling
                    parts = []
                    
                    # Get errors with column info, sorted by column
                    col_errors = sorted(
                        [e for e in errors if e.error_type == "syntax" and e.column > 0],
                        key=lambda e: e.column
                    )
                    
                    # Handle each error with column information
                    for error in col_errors:
                        col = max(0, error.column - 1)  # Convert to 0-based
                        
                        # Add text before the error
                        if col > current_pos:
                            parts.append((fragment.style, text[current_pos:col]))
                        
                        # Determine how much text to highlight (at least one character)
                        highlight_len = 1
                        
                        # If we have context, try to highlight the problematic token
                        if "'" in error.message:
                            # Extract token from error message like "invalid syntax: '...'"
                            token = error.message.split("'")[1] if "'" in error.message else None
                            
                            if token and token in text[col:]:
                                highlight_len = len(token)
                        
                        # Add the highlighted part
                        if col + highlight_len <= len(text):
                            parts.append((fragment.style + " class:syntax-error", 
                                           text[col:col+highlight_len]))
                            current_pos = col + highlight_len
                    
                    # Add any remaining text
                    if current_pos < len(text):
                        parts.append((fragment.style, text[current_pos:]))
                    
                    # Create fragments from parts
                    for style, part_text in parts:
                        if part_text:  # Skip empty parts
                            new_fragments.append(Fragment(part_text, style))
                else:
                    # For style errors or when we don't have column info,
                    # highlight the entire line
                    new_fragments.append(
                        Fragment(fragment.text, fragment.style + " class:syntax-error")
                    )
            else:
                # No error, keep original fragment
                new_fragments.append(fragment)
        
        return Transformation(new_fragments)

class FoldingProcessor(Processor):
    """Processor that handles folded regions of code"""
    
    def __init__(self, filename):
        self.filename = filename
        
    def apply_transformation(self, transformation_input):
        """Apply folding transformation to the displayed text"""
        buffer_control = transformation_input.buffer_control
        document = transformation_input.document
        lines = document.lines
        folded_regions = editor_state.folded_regions.get(self.filename, [])
        
        # No folded regions, no transformation needed
        if not folded_regions:
            return Transformation(transformation_input.fragments)
            
        # Create a new list of fragments with folded regions replaced
        new_fragments = []
        line_to_fragments = {}
        
        # Group fragments by line number
        for fragment in transformation_input.fragments:
            line = get_fragment_line(fragment, transformation_input)
            if line not in line_to_fragments:
                line_to_fragments[line] = []
            line_to_fragments[line].append(fragment)
        
        # Process each line
        for line_num in range(len(lines)):
            if line_num not in line_to_fragments:
                continue
                
            # Check if this line starts a folded region
            is_folded_start = False
            folded_end = None
            
            for start, end in folded_regions:
                if start == line_num:
                    is_folded_start = True
                    folded_end = end
                    break
            
            if is_folded_start and folded_end is not None:
                # Add the current line with a folding marker
                line_fragments = line_to_fragments[line_num]
                for fragment in line_fragments:
                    new_fragments.append(fragment)
                
                # Add a folding placeholder
                folded_count = folded_end - line_num
                fold_text = f" [... {folded_count} lines folded ...]"
                new_fragments.append(
                    Fragment(fold_text, "class:folded-code")
                )
                
                # Skip the folded lines
                line_num = folded_end
            else:
                # Not a folded region, add fragments normally
                fragments = line_to_fragments.get(line_num, [])
                new_fragments.extend(fragments)
        
        return Transformation(new_fragments)

def initialize_tabs(filename):
    """Initialize tabs with the provided filename"""
    # Clear any existing tabs
    editor_state.tabs = []
    
    # Add the initial tab
    tab = editor_state.add_tab(filename)
    
    # Now that get_lexer_for_file is defined, set the lexer
    tab.lexer = get_lexer_for_file(filename)
    
    # Load the file content if provided
    if filename:
        load_file(filename, tab.buffer)

# Store detailed insights per line for tooltips
class InsightTooltipState:
    """Tracks code insight tooltips state"""
    def __init__(self):
        self.tooltips = {}  # Map of (filename, line_number) to insight text
        self.active_tooltip = None  # (filename, line_number) of currently displayed tooltip
        self.show_tooltips = True  # Toggle for tooltip display
        self.hover_line = -1  # Line where cursor is currently hovering
        self.hover_insight_generated = False  # Whether an insight was generated for the hover line
        
        # Animation properties
        self.tooltip_opacity = 0.0  # Used for fade-in/fade-out animation
        self.tooltip_scale = 1.0  # Used for pop effect animation
        self.animating = False  # Flag indicating if animation is in progress
        self.animation_direction = "in"  # "in" for appearing, "out" for disappearing

# Add tooltip state to editor_state
editor_state.tooltips = InsightTooltipState()

# State for code completion popup
class CompletionState:
    """Tracks code completion popup state"""
    def __init__(self):
        self.completions = []  # List of available completions (strings or Snippet objects)
        self.current_index = 0  # Currently selected completion index
        self.visible = False  # Whether the popup is currently visible
        self.position = (0, 0)  # (row, column) position of the popup
        self.trigger_position = 0  # Cursor position when completion was triggered
        self.is_snippet = False  # Whether the current completion is a snippet
        self.active_snippet = None  # Currently active snippet if in snippet editing mode
        self.snippet_placeholders = []  # List of placeholder positions for the active snippet
        self.current_placeholder = 0  # Index of the current placeholder being edited
        
        # Animation properties
        self.opacity = 0.0  # Used for fade-in/fade-out animation
        self.scale = 1.0  # Used for pop effect animation
        self.animating = False  # Flag indicating if animation is in progress
        self.animation_direction = "in"  # "in" for appearing, "out" for disappearing

# Add completion state to editor_state
editor_state.completion = CompletionState()

class CompletionProcessor(Processor):
    """Processor that displays the code completion popup with animations"""
    
    def apply_transformation(self, transformation_input):
        """Apply transformation to display the code completion popup"""
        # Only process if completions are available and popup should be visible
        if not editor_state.completion.visible or not editor_state.completion.completions:
            return Transformation(transformation_input.fragments)
            
        document = transformation_input.document
        cursor_line = document.cursor_position_row
        cursor_col = document.cursor_position_col
        
        # Make sure we're on the right line where the popup should appear
        if cursor_line != editor_state.completion.position[0]:
            return Transformation(transformation_input.fragments)
        
        # Create a new list of fragments with completion popup
        new_fragments = []
        line_to_fragments = {}
        
        # Group fragments by line number
        for fragment in transformation_input.fragments:
            line = get_fragment_line(fragment, transformation_input)
            if line not in line_to_fragments:
                line_to_fragments[line] = []
            line_to_fragments[line].append(fragment)
        
        # Process each line
        for line in sorted(line_to_fragments.keys()):
            fragments = line_to_fragments[line]
            
            # Add the line's fragments
            for fragment in fragments:
                new_fragments.append(fragment)
            
            # If this is the line where the completion popup should appear
            if line == cursor_line:
                # Only show popup if opacity > 0.05 (animation threshold)
                if editor_state.completion.opacity > 0.05:
                    # Add completion popup
                    completions = editor_state.completion.completions
                    current_index = editor_state.completion.current_index
                    
                    # Calculate the column where the popup should start
                    popup_col = editor_state.completion.position[1]
                    
                    # Style based on animation state
                    base_style = "class:completion-popup"
                    opacity_style = f"{base_style} opacity:{editor_state.completion.opacity}"
                    scale_style = f" transform-scale:{editor_state.completion.scale}"
                    
                    # Add the popup box styling
                    popup_style = f"{opacity_style}{scale_style}"
                    
                    # Create popup with a box around it
                    popup_text = "┌" + "─" * 30 + "┐\n"
                    
                    # Add completions with highlighting for the selected one
                    for i, item in enumerate(completions):
                        # Handle snippet items differently
                        if isinstance(item, snippets.Snippet):
                            # Format as "prefix: description" or just "prefix" if no description
                            if item.description:
                                display_text = f"{item.prefix}: {item.description}"
                            else:
                                display_text = item.get_display_text()
                                
                            # Truncate if too long
                            if len(display_text) > 27:
                                display_text = display_text[:24] + "..."
                                
                            # Mark as a snippet with a special icon
                            if i == current_index:
                                popup_text += "│ > " + display_text.ljust(24) + " 📋│\n"
                            else:
                                popup_text += "│   " + display_text.ljust(24) + " 📋│\n"
                        else:
                            # Regular text completion
                            if i == current_index:
                                popup_text += "│ > " + str(item).ljust(27) + "│\n"
                            else:
                                popup_text += "│   " + str(item).ljust(27) + "│\n"
                    
                    popup_text += "└" + "─" * 30 + "┘"
                    
                    # Add popup to the end of the line, but position it at the cursor
                    popup_indent = " " * popup_col  # Indent to cursor position
                    new_fragments.append(Fragment(popup_indent + popup_text, popup_style))
        
        return Transformation(new_fragments)

class InsightTooltipProcessor(Processor):
    """Processor that adds interactive tooltips to code insights"""
    
    def apply_transformation(self, transformation_input):
        """Apply transformation to show tooltips"""
        if not editor_state.tooltips.show_tooltips:
            return Transformation(transformation_input.fragments)
            
        document = transformation_input.document
        cursor_line = document.cursor_position_row
        active_tab = editor_state.get_active_tab()
        
        # If cursor moved to a new line, update hover line
        if cursor_line != editor_state.tooltips.hover_line:
            # Check if we need to animate out an existing tooltip
            old_line = editor_state.tooltips.hover_line
            if old_line >= 0 and active_tab and active_tab.filename:
                old_tooltip_key = (active_tab.filename, old_line)
                if old_tooltip_key in editor_state.tooltips.tooltips:
                    # Start a pop-out animation for the old tooltip
                    import pop_animation
                    animation_name = f"tooltip_pop_out_{old_tooltip_key}"
                    
                    # Create or update the pop-out animation
                    if animation_name not in animations.animation_manager.animations:
                        # Create a combined pop-out animation with enhanced parameters
                        pop_out = pop_animation.PopOutAnimation(
                            editor_state.tooltips,
                            "tooltip_opacity",
                            "tooltip_scale",
                            on_update=lambda v: refresh_editor_view(),
                            on_complete=lambda: setattr(editor_state.tooltips, 'animating', False),
                            start_scale=1.0,
                            end_scale=0.9,
                            duration=0.2,
                            easing='ease_in_quad'
                        )
                        
                        # Add to animation manager
                        class PopOutAnimationWrapper(animations.AnimationState):
                            def __init__(self, pop_animation):
                                super().__init__()
                                self.pop_animation = pop_animation
                                self.duration = pop_animation.duration
                                
                            def start(self):
                                """Start the pop animation"""
                                self.animating = True
                                self.pop_animation.start()
                                
                            def stop(self):
                                """Stop the pop animation"""
                                self.animating = False
                                self.pop_animation.stop()
                                
                        wrapper = PopOutAnimationWrapper(pop_out)
                        animations.animation_manager.add_animation(animation_name, wrapper)
                    
                    # Start the animation
                    animations.animation_manager.start_animation(animation_name)
                    editor_state.tooltips.animating = True
                    editor_state.tooltips.animation_direction = "out"
            
            # Update to the new hover line
            editor_state.tooltips.hover_line = cursor_line
            editor_state.tooltips.hover_insight_generated = False
            
            # Initialize animation state for new line (will be shown with pop-in animation)
            editor_state.tooltips.tooltip_opacity = 0.0
            editor_state.tooltips.tooltip_scale = 1.0
            
            # Get tooltip for this line if available
            if active_tab and active_tab.filename:
                tooltip_key = (active_tab.filename, cursor_line)
                # If we don't have insight for this line yet, request it
                if tooltip_key not in editor_state.tooltips.tooltips and not editor_state.tooltips.hover_insight_generated:
                    # Request analysis only if we're not already analyzing
                    if not editor_state.analyzing_code:
                        # Request line-specific analysis
                        editor_state.tooltips.hover_insight_generated = True
                        # Store current cursor position for analysis
                        buffer_text = document.text
                        threading.Thread(
                            target=lambda: request_hover_analysis(buffer_text, cursor_line, active_tab.filename),
                            daemon=True
                        ).start()
                # If we have this tooltip, start animation if not already animating
                elif tooltip_key in editor_state.tooltips.tooltips and not editor_state.tooltips.animating:
                    # Import pop animation
                    import pop_animation
                    
                    # Start pop-in animation with combined fade and scale effects
                    editor_state.tooltips.animating = True
                    editor_state.tooltips.animation_direction = "in"
                    
                    # Find or create tooltip animations
                    animation_name = f"tooltip_pop_{tooltip_key}"
                    if animation_name not in animations.animation_manager.animations:
                        # Create a combined pop-in animation with enhanced parameters
                        pop_anim = pop_animation.PopInAnimation(
                            editor_state.tooltips,
                            "tooltip_opacity",
                            "tooltip_scale",
                            on_update=lambda v: refresh_editor_view(),
                            start_scale=1.05,  # Start slightly larger
                            end_scale=1.0,     # End at normal scale
                            duration=0.28,     # Quick but visible animation
                            easing='ease_out_cubic'  # Smoother ease out
                        )
                        # Add to animation manager with a custom wrapper
                        class PopAnimationWrapper(animations.AnimationState):
                            def __init__(self, pop_animation):
                                super().__init__()
                                self.pop_animation = pop_animation
                                self.duration = pop_animation.duration
                                
                            def start(self):
                                """Start the pop animation"""
                                self.animating = True
                                self.pop_animation.start()
                                
                            def stop(self):
                                """Stop the pop animation"""
                                self.animating = False
                                self.pop_animation.stop()
                                
                            def on_complete(self):
                                """Called when animation completes"""
                                # Keep the tooltip fully visible after animation
                                editor_state.tooltips.tooltip_opacity = 1.0
                                editor_state.tooltips.tooltip_scale = 1.0
                                editor_state.tooltips.animating = False
                        
                        # Add the wrapped animation to the manager
                        wrapper = PopAnimationWrapper(pop_anim)
                        animations.animation_manager.add_animation(animation_name, wrapper)
                    
                    # Start the animation
                    animations.animation_manager.start_animation(animation_name)
        
        # Create a new list of fragments with tooltips
        new_fragments = []
        line_to_fragments = {}
        
        # Group fragments by line number
        for fragment in transformation_input.fragments:
            line = get_fragment_line(fragment, transformation_input)
            if line not in line_to_fragments:
                line_to_fragments[line] = []
            line_to_fragments[line].append(fragment)
        
        # Find if there's an active tooltip
        has_active_tooltip = False
        active_tooltip_line = -1
        active_tooltip_text = None
        
        if active_tab and active_tab.filename:
            active_tooltip_key = (active_tab.filename, cursor_line)
            if active_tooltip_key in editor_state.tooltips.tooltips:
                has_active_tooltip = True
                active_tooltip_line = cursor_line
                active_tooltip_text = editor_state.tooltips.tooltips[active_tooltip_key]
        
        # Process each line
        for line in sorted(line_to_fragments.keys()):
            fragments = line_to_fragments[line]
            
            # Add the line's fragments
            for fragment in fragments:
                new_fragments.append(fragment)
            
            # If this is the line with an active tooltip, add it
            if has_active_tooltip and line == active_tooltip_line:
                # Apply animation to tooltip only if it's visible enough
                if editor_state.tooltips.tooltip_opacity > 0.05:
                    # Create a visible tooltip with the insight
                    tooltip_prefix = " → "
                    tooltip_style = f"class:insight-tooltip"
                    
                    # Scale the text for pop effect (if scale animation is active)
                    scale_effect = ""
                    if editor_state.tooltips.tooltip_scale != 1.0:
                        # Apply scale effect through styling
                        scale_effect = f" transform-scale:{editor_state.tooltips.tooltip_scale}"
                    
                    # Apply opacity through styling
                    opacity_style = f"{tooltip_style} opacity:{editor_state.tooltips.tooltip_opacity}{scale_effect}"
                    
                    # Add tooltip at the end of the line with slight indentation
                    new_fragments.append(Fragment(tooltip_prefix + active_tooltip_text, opacity_style))
        
        return Transformation(new_fragments)


def refresh_editor_view():
    """Force refresh of the editor view to reflect animation changes"""
    # This is called from animation callbacks to refresh the UI
    try:
        if editor_app and editor_app.invalidate:
            editor_app.invalidate()
    except (NameError, AttributeError):
        # app might not be accessible or initialized yet
        pass

def request_hover_analysis(text, line_number, filename):
    """Request code analysis for hovering over a specific line"""
    import ai_context
    
    try:
        # Get context for this specific line
        context = ai_context.get_code_context(text, line_number)
        if context:
            # Add filename to context
            context['filename'] = filename
            
            # Generate a concise insight for tooltips
            insight = generate_tooltip_insight(context)
            
            # Store in tooltips dictionary
            if insight:
                with analysis_lock:
                    editor_state.tooltips.tooltips[(filename, line_number)] = insight
    except Exception as e:
        print(f"Error generating tooltip insight: {str(e)}", file=sys.stderr)

def generate_tooltip_insight(context):
    """Generate a concise insight for tooltips"""
    import ai_context
    
    context_type = context['context_type']
    current_line = context['current_line']
    
    # Generate shorter, more focused insights for tooltips
    try:
        if context_type == 'function_definition':
            # Extract function name and parameters
            match = re.search(r'def\s+(\w+)\s*\((.*?)\):', current_line)
            if match:
                func_name = match.group(1)
                params = match.group(2).strip()
                return f"Function '{func_name}' with params: {params or 'none'}"
        elif context_type == 'class_definition':
            # Extract class name
            match = re.search(r'class\s+(\w+)', current_line)
            if match:
                class_name = match.group(1)
                return f"Class '{class_name}' definition"
        elif context_type == 'loop_construct':
            if 'for ' in current_line:
                match = re.search(r'for\s+(\w+)\s+in\s+(.*?):', current_line)
                if match:
                    var_name = match.group(1)
                    iterable = match.group(2).strip()
                    return f"Loop over {iterable} using '{var_name}'"
            elif 'while ' in current_line:
                match = re.search(r'while\s+(.*?):', current_line)
                if match:
                    condition = match.group(1).strip()
                    return f"While loop with condition: {condition}"
        elif context_type == 'conditional':
            if 'if ' in current_line:
                match = re.search(r'if\s+(.*?):', current_line)
                if match:
                    condition = match.group(1).strip()
                    return f"Conditional: {condition}"
            elif 'elif ' in current_line:
                match = re.search(r'elif\s+(.*?):', current_line)
                if match:
                    condition = match.group(1).strip()
                    return f"Elif condition: {condition}"
            elif 'else:' in current_line:
                return "Else block"
        elif context_type == 'import_statement':
            return f"Import: {current_line.strip()}"
        elif context_type == 'variable_assignment':
            match = re.search(r'(\w+)\s*=\s*(.*)', current_line)
            if match:
                var_name = match.group(1)
                value = match.group(2).strip()
                return f"Variable '{var_name}' = {value}"
    except Exception as e:
        print(f"Error generating tooltip: {str(e)}", file=sys.stderr)
    
    # Default
    return current_line.strip()

# Analysis lock for thread-safe operations 
analysis_lock = threading.Lock()

def get_insights_panel():
    """Create the AI code insights panel"""
    def get_insight_text():
        if editor_state.analyzing_code:
            return [("class:insight.analyzing", " Analyzing code... ")]
        elif editor_state.current_insight:
            # Format the insight text with added styling
            lines = editor_state.current_insight.split(". ")
            formatted_text = []
            
            for i, line in enumerate(lines):
                if i > 0:
                    formatted_text.append(("", ". "))  # Add the period back
                
                # Apply special formatting for recommendations
                if "Consider" in line or "suggestion" in line.lower():
                    formatted_text.append(("class:insight.suggestion", line))
                elif "complexity" in line.lower() or "detected" in line.lower():
                    formatted_text.append(("class:insight.warning", line))
                else:
                    formatted_text.append(("class:insight.content", line))
            
            # Add instruction for tooltip functionality at the end
            formatted_text.append(("", "\n"))
            formatted_text.append(("class:insight.tip", " Tip: Hover over code lines for contextual insights (Alt+T to toggle) "))
            
            return formatted_text
        else:
            return [
                ("class:insight.empty", " No code insights available. Press Alt+I to analyze current code. "),
                ("", "\n"),
                ("class:insight.tip", " Tip: Insights are automatically generated when you hover over code (Alt+T to toggle) ")
            ]
    
    return Window(
        content=FormattedTextControl(get_insight_text),
        height=4,  # Increased height to accommodate multi-line insights
        wrap_lines=True,
        style="class:insight-panel",
    )

def create_search_panel():
    """Create the search and replace panel"""
    # Create the search input field
    search_field = TextArea(
        height=1,
        prompt="Search: ",
        style="class:search.field",
        multiline=False,
        wrap_lines=False,
        focus_on_click=True,
    )
    
    # Create the replace input field
    replace_field = TextArea(
        height=1,
        prompt="Replace: ",
        style="class:replace.field",
        multiline=False,
        wrap_lines=False,
        focus_on_click=True,
    )
    
    # Create buttons
    # Define the helper functions first to avoid UnboundLocalError
    def goto_next_match():
        result = editor_state.goto_next_search_result()
        if result:
            active_tab = editor_state.get_active_tab()
            if active_tab:
                start, end = result
                active_tab.buffer.cursor_position = start
                index = editor_state.current_search_index + 1
                count = len(editor_state.search_results)
                editor_state.status_message = f"Match {index} of {count}"
    
    def goto_prev_match():
        result = editor_state.goto_prev_search_result()
        if result:
            active_tab = editor_state.get_active_tab()
            if active_tab:
                start, end = result
                active_tab.buffer.cursor_position = start
                index = editor_state.current_search_index + 1
                count = len(editor_state.search_results)
                editor_state.status_message = f"Match {index} of {count}"
    
    def replace_current(text):
        success = editor_state.replace_current_match(text)
        if success:
            editor_state.status_message = "Replaced match"
            editor_state.status_type = "info"
            # Go to next match if any
            goto_next_match()
        else:
            editor_state.status_message = "No current match to replace"
            editor_state.status_type = "warning"
    
    def replace_all(text):
        count = editor_state.replace_all_matches(text)
        if count > 0:
            editor_state.status_message = f"Replaced {count} matches"
            editor_state.status_type = "info"
        else:
            editor_state.status_message = "No matches to replace"
            editor_state.status_type = "warning"

    # When actions are triggered, we need to update the editor state
    def perform_search_action(text):
            case_sensitive = case_checkbox.checked
            results = editor_state.perform_search(text, case_sensitive)
            count = len(results)
            if count > 0:
                editor_state.status_message = f"Found {count} matches"
                editor_state.status_type = "info"
                # Position cursor at the first match
                if results:
                    active_tab = editor_state.get_active_tab()
                    if active_tab:
                        start, end = results[0]
                        active_tab.buffer.cursor_position = start
            else:
                editor_state.status_message = "No matches found"
                editor_state.status_type = "warning"
    
    # Create buttons now that the functions are defined
    search_button = Button(
        text="Search",
        handler=lambda: perform_search_action(search_field.text),
        width=8,
    )
    
    next_button = Button(
        text="Next",
        handler=goto_next_match,
        width=8,
    )
    
    prev_button = Button(
        text="Prev",
        handler=goto_prev_match,
        width=8,
    )
    
    replace_button = Button(
        text="Replace",
        handler=lambda: replace_current(replace_field.text),
        width=8,
    )
    
    replace_all_button = Button(
        text="Replace All",
        handler=lambda: replace_all(replace_field.text),
        width=12,
    )
    
    case_checkbox = Checkbox(
        text="Case sensitive", 
        checked=False,
    )
    
    # Arrange buttons in horizontal containers
    search_buttons = HSplit([
        VSplit([
            search_field,
            search_button,
            next_button,
            prev_button,
        ]),
        VSplit([
            replace_field,
            replace_button,
            replace_all_button,
            case_checkbox,
        ]),
    ])
    
    return Frame(
        search_buttons,
        title="Search & Replace",
        style="class:search-panel",
    )

def create_editor_layout(terminal_manager, filename=None):
    """Create the main editor layout"""
    # Import adaptive UI
    from adaptive_ui import get_adaptive_ui
    
    # Initialize tabs with the given filename
    initialize_tabs(filename)
    
    # Get adaptive UI manager
    adaptive_ui = get_adaptive_ui()
    
    # Start terminal size monitoring
    adaptive_ui.start_terminal_monitor()
    
    # Get terminal dimensions
    terminal_width, terminal_height = adaptive_ui.get_terminal_size()
    
    # Get UI size category
    size_category = adaptive_ui._determine_size_category(terminal_width, terminal_height)
    
    # Store current size info in editor state
    editor_state.terminal_width = terminal_width
    editor_state.terminal_height = terminal_height
    editor_state.ui_size_category = size_category
    
    # Tab bar at the top
    tab_bar = create_tab_bar()
    
    # Dynamic editor window (changes based on active tab)
    editor_window = get_active_editor_window()
    
    # Calculate panel heights based on available space
    # Account for tab bar (1) and status bar (1)
    available_height = terminal_height - 2
    
    # Define which panels are enabled
    panels = {
        "editor": True,  # Editor is always shown
        "terminal": editor_state.show_terminal,
        "insights": editor_state.show_insights,
        "search": getattr(editor_state, "show_search_ui", False),
        "tab_bar": True,  # Tab bar is always shown
        "status_bar": True  # Status bar is always shown
    }
    
    # Get optimal panel heights
    panel_heights = adaptive_ui.get_panel_sizes(available_height, panels)
    
    # Terminal output window with adaptive height
    terminal_window = Window(
        content=FormattedTextControl(
            text=lambda: terminal_manager.get_formatted_output()
        ),
        wrap_lines=True,
        height=panel_heights["terminal"],
    )
    
    # AI Insights panel with adaptive height
    insights_panel = get_insights_panel()
    if panel_heights["insights"] > 0:
        insights_panel.height = panel_heights["insights"]
    
    # Status bar
    status_bar = Window(
        height=1,
        content=FormattedTextControl(
            create_status_bar_text
        ),
        style="class:status-bar",
    )
    
    # Search & Replace panel with adaptive height
    search_panel = create_search_panel()
    # Allow search panel to be smaller in small screens
    if panel_heights["search"] > 0 and hasattr(search_panel, "height"):
        search_panel.height = panel_heights["search"]
    
    # Create the layout with conditional containers
    terminal_container = ConditionalContainer(
        content=Frame(terminal_window, title="Terminal Output"),
        filter=Condition(lambda: editor_state.show_terminal)
    )
    
    insights_container = ConditionalContainer(
        content=Frame(insights_panel, title="AI Code Insights"),
        filter=Condition(lambda: editor_state.show_insights)
    )
    
    search_container = ConditionalContainer(
        content=search_panel,
        filter=Condition(lambda: getattr(editor_state, "show_search_ui", False))
    )
    
    # Register resize callback
    def on_terminal_resize(width, height, size_category, category_changed):
        editor_state.terminal_width = width
        editor_state.terminal_height = height
        editor_state.ui_size_category = size_category
        if category_changed:
            # Get new panel heights
            new_panel_heights = adaptive_ui.get_panel_sizes(height - 2, panels)
            
            # Update panel heights
            if hasattr(terminal_window, "height"):
                terminal_window.height = new_panel_heights["terminal"]
            if hasattr(insights_panel, "height"):
                insights_panel.height = new_panel_heights["insights"]
            if hasattr(search_panel, "height"):
                search_panel.height = new_panel_heights["search"]
            
            # Force UI refresh
            try:
                from prompt_toolkit.application import get_app
                get_app().invalidate()
            except:
                pass
    
    adaptive_ui.register_resize_callback(on_terminal_resize)
    
    return HSplit([
        tab_bar,
        Frame(editor_window, title="Editor"),
        search_container,
        insights_container,
        terminal_container,
        status_bar,
    ])
