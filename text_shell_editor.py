#!/usr/bin/env python3
"""
TextShellEditor - A terminal-based text editor with integrated shell functionality.
Main entry point for the application.
"""

# Define editor_app at module level for animation callbacks
editor_app = None

import os
import sys
import argparse
import logging
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.styles import Style

# Set up logging
logger = logging.getLogger(__name__)

from editor_core import create_editor_layout, check_auto_save, editor_state
from key_bindings import create_key_bindings
from terminal_manager import TerminalManager
from utils import get_available_shells
from themes import get_theme_style, get_available_themes
import syntax_checker  # Import to initialize syntax checking
from config_manager import get_config, load_command_line_config
from adaptive_ui import get_adaptive_ui  # Import adaptive UI functionality
import ai_snippets  # Import AI-powered snippet functionality

def apply_config_to_editor_state(config):
    """Apply configuration settings to the editor state
    
    Args:
        config: ConfigManager instance
    """
    # Apply theme settings
    theme_name = config.get('theme', 'dracula')
    editor_state.current_theme = theme_name
    
    # Apply general UI settings
    editor_state.wrap_lines = config.get('wrap_lines', True)  # Match EditorState default
    editor_state.line_numbers = config.get('line_numbers', True)
    editor_state.folding_enabled = config.get('folding_enabled', True)
    editor_state.show_insights = config.get('show_insights', True)
    
    # Apply auto-save settings
    editor_state.auto_save_enabled = config.get('auto_save', True)
    
    # Get and validate auto-save interval
    auto_save_interval = config.get('auto_save_interval', 30)
    # Ensure interval is within valid range
    if not isinstance(auto_save_interval, int) or auto_save_interval < 5:
        auto_save_interval = 5  # Minimum 5 seconds
        logger.warning("Auto-save interval too low, setting to minimum 5 seconds")
    elif auto_save_interval > 300:
        auto_save_interval = 300  # Maximum 5 minutes
        logger.warning("Auto-save interval too high, setting to maximum 300 seconds")
    editor_state.auto_save_interval = auto_save_interval
    
    # Apply syntax checking settings
    editor_state.syntax_check_enabled = config.get('syntax_check', True)
    
    # Set the theme (already handled in main() but keeping reference here)
    # editor_state.theme = config.get('theme', 'default')
    
    # Set terminal height (this will be used when creating the layout)
    editor_state.terminal_height = config.get('terminal_height', 8)
    
    # Get and validate tab size
    if hasattr(editor_state, 'tab_size'):
        tab_size = config.get('tab_size', 4)
        # Ensure tab size is within valid range
        if not isinstance(tab_size, int) or tab_size < 2:
            tab_size = 2  # Minimum 2 spaces
            logger.warning("Tab size too small, setting to minimum 2 spaces")
        elif tab_size > 8:
            tab_size = 8  # Maximum 8 spaces
            logger.warning("Tab size too large, setting to maximum 8 spaces")
        editor_state.tab_size = tab_size
    
    # Set whether to use spaces for indentation
    if hasattr(editor_state, 'use_spaces'):
        editor_state.use_spaces = config.get('use_spaces', True)
        logger.debug(f"Using {'spaces' if editor_state.use_spaces else 'tabs'} for indentation")

def check_terminal_size():
    """Check if terminal size is adequate for the editor"""
    try:
        # Get terminal size
        terminal_width, terminal_height = os.get_terminal_size()
        
        min_width = 80
        min_height = 24
        
        if terminal_width < min_width or terminal_height < min_height:
            print(f"Warning: Terminal window too small. Minimum size: {min_width}x{min_height}")
            print(f"Current size: {terminal_width}x{terminal_height}")
            print("For the best experience, please resize your terminal.")
            return False
        
        return True
    except OSError:
        # If we can't determine the size, we'll just proceed
        print("Warning: Unable to determine terminal size.")
        return True

def print_demo_help():
    """Display help information for demo mode"""
    print("\nTextShellEditor - Demo Mode")
    print("==========================")
    print("\nThis is a simplified demo showing the editor's features.")
    print("For the full experience, use a terminal size of at least 80x24.")
    print("\nFeatures implemented:")
    print("  * Multi-tab editing with visual tab bar")
    print("  * Integrated terminal with command execution")
    print("  * Syntax highlighting for various languages")
    print("  * AI-powered code context insights")
    print("  * Intelligent code completion with animations")
    print("  * Customizable key bindings")
    print("  * Theme selection (5 built-in themes)")
    print("  * Smart auto-indentation for code")
    print("  * Robust configuration system")
    print("\nKey commands:")
    print("  * Ctrl+N: New tab")
    print("  * Ctrl+W: Close tab")
    print("  * Ctrl+Left/Right: Navigate tabs")
    print("  * Alt+1-9: Switch to specific tab")
    print("  * Ctrl+S: Save file")
    print("  * Alt+Enter: Execute command")
    print("  * Ctrl+I: Toggle AI insights panel")
    print("  * Alt+I: Analyze code at cursor position")
    print("  * Alt+H: Toggle code insight tooltips")
    print("  * Ctrl+Space: Show code completion suggestions")
    print("  * Tab/Shift+Tab: Navigate completions")
    print("  * Alt+W: Toggle line wrapping")
    print("  * Alt+N: Toggle line numbers")
    print("  * Alt+A: Toggle auto-save feature")
    print("  * Alt+F: Toggle code folding")
    print("  * Alt+Z: Toggle fold at cursor position")
    print("  * Alt+C: Toggle syntax checking")
    print("  * Alt+S: Check syntax on current file")
    print("  * Ctrl+F: Toggle search & replace panel")
    print("  * F3/Shift+F3: Find next/previous match")
    print("  * Ctrl+Q: Exit")
    print("  * F1: Help")
    print("  * Enter: Auto-indents based on context")
    print("\nConfiguration Options:")
    print("  --theme THEME               Select theme (default, monokai, etc.)")
    print("  --wrap-lines, --no-wrap-lines   Enable/disable line wrapping")
    print("  --line-numbers, --no-line-numbers   Show/hide line numbers")
    print("  --tab-size N                Set tab size for indentation (2-8 spaces)")
    print("  --use-tabs, --use-spaces    Choose tabs or spaces for indentation")
    print("  --auto-save, --no-auto-save   Enable/disable auto-save")
    print("  --auto-save-interval N      Set auto-save interval in seconds (5-300)")
    print("  --syntax-check, --no-syntax-check   Enable/disable syntax checking")
    print("  --shell SHELL               Select shell type (bash, zsh, cmd)")
    print("  --edit-config               Open the config file for editing")
    print("  --create-config             Create a default configuration file")
    print("  --validate-config           Validate config file and show current settings")
    print("  --export-config PATH        Export configuration to a different file")
    print("  --list-themes               List all available themes")
    print("\nFor more details, see the README.md file.")
    print("\nPress Enter to exit the demo...")

def main():
    parser = argparse.ArgumentParser(description="TextShellEditor - A text editor with integrated terminal capabilities")
    parser.add_argument('file', nargs='?', help="File to open")
    
    # Shell and theme options
    parser.add_argument('--shell', '-s', choices=get_available_shells(), default=None,
                       help="Specify shell to use (defaults to system default)")
    parser.add_argument('--theme', '-t', choices=get_available_themes(), default=None,
                       help="Specify theme to use (overrides config file)")
                       
    # UI preferences
    parser.add_argument('--wrap-lines', dest='wrap_lines', action='store_true', help="Enable line wrapping")
    parser.add_argument('--no-wrap-lines', dest='wrap_lines', action='store_false', help="Disable line wrapping")
    parser.add_argument('--line-numbers', dest='line_numbers', action='store_true', help="Show line numbers")
    parser.add_argument('--no-line-numbers', dest='line_numbers', action='store_false', help="Hide line numbers")
    parser.add_argument('--tab-size', type=int, help="Set tab size for indentation (2-8 spaces)")
    parser.add_argument('--use-tabs', dest='use_spaces', action='store_false', help="Use tabs for indentation")
    parser.add_argument('--use-spaces', dest='use_spaces', action='store_true', help="Use spaces for indentation")
    
    # Feature toggles
    parser.add_argument('--auto-save', dest='auto_save', action='store_true', help="Enable auto-save")
    parser.add_argument('--no-auto-save', dest='auto_save', action='store_false', help="Disable auto-save")
    parser.add_argument('--auto-save-interval', type=int, help="Set auto-save interval in seconds (5-300)")
    parser.add_argument('--syntax-check', dest='syntax_check', action='store_true', help="Enable syntax checking")
    parser.add_argument('--no-syntax-check', dest='syntax_check', action='store_false', help="Disable syntax checking")
    
    # Configuration and help options
    parser.add_argument('--config', '-c', help="Path to custom config file")
    parser.add_argument('--create-config', action='store_true', help="Create a default configuration file")
    parser.add_argument('--edit-config', '-e', action='store_true', help="Open configuration file for editing")
    parser.add_argument('--validate-config', '-v', action='store_true', help="Validate the configuration file and report any errors")
    parser.add_argument('--export-config', help="Export the configuration to a specified file path")
    parser.add_argument('--list-themes', '-l', action='store_true', help="List available themes and exit")
    parser.add_argument('--demo', '-d', action='store_true', help="Run in demo mode (displays feature information)")
    
    # Set defaults for boolean flags to None so we can detect if they were specified
    parser.set_defaults(wrap_lines=None, line_numbers=None, auto_save=None, syntax_check=None, use_spaces=None)
    args = parser.parse_args()
    
    # Load configuration from file
    config = get_config(args.config)
    
    # Create default config if requested
    if args.create_config:
        success = config.save()
        if success:
            print(f"Default configuration file created at: {config.config_path}")
        else:
            print("Error creating configuration file. Check permissions and try again.")
        return
    
    # Export configuration if requested
    if args.export_config:
        export_path = args.export_config
        
        # Make sure we have an absolute path
        if not os.path.isabs(export_path):
            export_path = os.path.abspath(export_path)
            
        print(f"Exporting configuration to: {export_path}")
        
        # Make sure we're not overwriting the original without warning
        if os.path.normpath(export_path) == os.path.normpath(config.config_path):
            print(f"Warning: Export path is the same as the current config file.")
            print(f"The current configuration file will be overwritten.")
            confirmation = input("Continue? (y/N): ").strip().lower()
            if confirmation != 'y':
                print("Export cancelled.")
                return
        
        # Export the configuration
        success = config.export(export_path)
        if success:
            print(f"Configuration exported to: {export_path}")
        else:
            print(f"Error exporting configuration to: {export_path}")
        return
    
    # Validate configuration if requested
    if args.validate_config:
        print(f"\nValidating configuration file: {config.config_path}")
        
        # If file doesn't exist, notify user
        if not os.path.exists(config.config_path):
            print("Configuration file doesn't exist. Run --create-config to create a default one.")
            return
            
        # Validate the config
        is_valid, errors = config.validate_config()
        
        if is_valid:
            print("Configuration is valid.")
            
            # Show current config values
            print("\nCurrent Configuration:")
            print("---------------------")
            for key, value in sorted(config.get_all().items()):
                if isinstance(value, dict):
                    print(f"{key}: <complex value>")
                else:
                    print(f"{key}: {value}")
        else:
            print("Configuration has errors:")
            for key, error in errors.items():
                print(f"  - {key}: {error}")
            print("\nRun with --create-config to create a new default configuration,")
            print("or --edit-config to fix the issues in your existing configuration.")
        return
    
    # If user requested to list themes, show them and exit
    if args.list_themes:
        print("\nAvailable Themes:")
        print("----------------")
        for theme in get_available_themes():
            print(f"  - {theme}")
        print("\nUse with: python text_shell_editor.py --theme THEME_NAME")
        print(f"\nCurrent theme (from config): {config.get('theme')}")
        return

    # Check terminal size early
    has_adequate_size = check_terminal_size()
    
    # Open config file for editing if requested
    if args.edit_config:
        # Ensure the config file exists
        if not os.path.exists(config.config_path):
            config.save()
        
        # Check if terminal size is adequate for editing
        if not has_adequate_size:
            print(f"Configuration file is located at: {config.config_path}")
            print("Please edit it with your preferred text editor.")
            return
        
        # Use our own editor to edit the config file
        args.file = config.config_path
        print(f"Opening configuration file: {config.config_path}")
        # Continue with regular startup to edit the file
    
    # Override config with command line arguments
    load_command_line_config(args)
    
    # If terminal size is inadequate or demo mode is requested, show the demo
    if args.demo or not has_adequate_size:
        print_demo_help()
        input()  # Wait for user to press Enter
        return
    
    # Apply configuration to editor state
    apply_config_to_editor_state(config)
    
    # Initialize terminal manager with configured shell
    terminal_manager = TerminalManager(shell_type=config.get('default_shell'))
    
    # Create the layout
    layout = create_editor_layout(terminal_manager, filename=args.file)
    
    # Define styles from theme
    # Use theme from editor state (which is already populated from config or command line)
    theme_name = editor_state.current_theme
    if not isinstance(theme_name, str):
        theme_name = 'dracula'  # Default fallback
    style = get_theme_style(theme_name)
    
    # Initialize animation system
    # Import animations module
    import animations
    
    # Initialize animation properties in editor_state
    editor_state.insights_panel_opacity = 1.0
    editor_state.search_panel_opacity = 1.0
    editor_state.terminal_panel_opacity = 1.0
    editor_state.refresh_required = False
    
    # Make sure editor_app is accessible globally
    
    # Set up animation for panel transitions
    # Create animations for insights panel
    insights_panel_animation = animations.FadeAnimation(
        editor_state, 
        "insights_panel_opacity", 
        0.0, 
        1.0,
        on_update=lambda v: editor_invalidate()
    )
    animations.animation_manager.add_animation("insights_panel_fade", insights_panel_animation)
    
    # Create animations for search panel
    search_panel_animation = animations.FadeAnimation(
        editor_state, 
        "search_panel_opacity", 
        0.0, 
        1.0,
        on_update=lambda v: editor_invalidate()
    )
    animations.animation_manager.add_animation("search_panel_fade", search_panel_animation)
    
    # Create animations for terminal panel
    terminal_panel_animation = animations.FadeAnimation(
        editor_state, 
        "terminal_panel_opacity", 
        0.0, 
        1.0,
        on_update=lambda v: editor_invalidate()
    )
    animations.animation_manager.add_animation("terminal_panel_fade", terminal_panel_animation)
    
    # This comment is no longer needed as we declare editor_app at the top with global
    
    # Helper function to refresh UI during animations
    def editor_invalidate():
        try:
            if editor_app and hasattr(editor_app, 'invalidate'):
                editor_app.invalidate()
        except (NameError, AttributeError):
            pass  # app might not be accessible or initialized yet
    
    # Create and run the application
    app = Application(
        layout=Layout(layout),
        key_bindings=create_key_bindings(terminal_manager),
        full_screen=True,
        mouse_support=True,
        style=style,
        # Enable automatic redrawing on terminal resize
        refresh_interval=0.5,  # Check for resize every 0.5 seconds
    )
    
    # Set the app variable for animation callbacks
    editor_app = app
    
    # Create a custom run loop for auto-save functionality
    try:
        # Create a done event to track when application should exit
        done = [False]
        
        # Define a custom refresh function to handle auto-save
        def auto_save_refresh():
            # Check if files need auto-saving
            check_auto_save()
            
            # Return False to continue running, True to exit
            return done[0]
        
        # Use asyncio for background timer since refresh_interval is not available
        import asyncio

        def auto_save_timer():
            if not done[0]:
                check_auto_save()
                # Schedule next auto-save check
                loop = asyncio.get_event_loop()
                loop.call_later(0.5, auto_save_timer)

        # Create and get the event loop and schedule the first auto-save check
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Create a new event loop if there's no current one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.call_later(0.5, auto_save_timer)

        # Run the application without the unsupported parameters
        app.run(pre_run=lambda: None, handle_sigint=True)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass
    finally:
        # Clean up resources
        terminal_manager.cleanup()
        syntax_checker.shutdown_checker()

if __name__ == "__main__":
    main()
