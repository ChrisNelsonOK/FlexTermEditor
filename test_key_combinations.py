#!/usr/bin/env python3

from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPress
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl

def print_all_keys_enum():
    """Print all available keys in the Keys enum."""
    print("=== All Keys in prompt-toolkit Keys enum ===")
    all_keys = [k for k in dir(Keys) if not k.startswith('_')]
    
    # Print with categorization
    function_keys = [k for k in all_keys if k.startswith('F') and k[1:].isdigit()]
    shift_keys = [k for k in all_keys if 'Shift' in k]
    control_keys = [k for k in all_keys if k.startswith('Control')]
    alt_keys = [k for k in all_keys if 'Alt' in k or 'Meta' in k]
    other_keys = [k for k in all_keys if k not in function_keys + shift_keys + control_keys + alt_keys]
    
    print(f"\nFunction keys ({len(function_keys)}):")
    for k in sorted(function_keys):
        print(f"  {k}")
    
    print(f"\nShift keys ({len(shift_keys)}):")
    for k in sorted(shift_keys):
        print(f"  {k}")
    
    print(f"\nControl keys ({len(control_keys)}):")
    for k in sorted(control_keys):
        print(f"  {k}")
    
    print(f"\nAlt/Meta keys ({len(alt_keys)}):")
    for k in sorted(alt_keys):
        print(f"  {k}")
    
    print(f"\nOther keys ({len(other_keys)}):")
    for k in sorted(other_keys):
        print(f"  {k}")

def test_key_bindings():
    """Test various key binding formats to see which ones work."""
    print("\n=== Testing key binding formats ===")
    
    kb = KeyBindings()
    
    # Test different formats for key combinations
    key_combinations = [
        # Function keys
        'f1', 'f2', 'f3', 'f12',
        
        # Shift combinations
        's-f3', 'shift+f3', 'S-f3', 'S+f3',
        's-a', 's-b', 'shift+a', 'shift+b',
        
        # Control combinations
        'c-f3', 'ctrl+f3', 'control+f3',
        'c-a', 'ctrl+a', 'control+a',
        
        # Alt combinations
        'a-f3', 'alt+f3', 'meta+f3', 'm-f3',
        'a-a', 'alt+a', 'meta+a', 'm-a',
        ('escape', 'f3'), ('escape', 'a'),
        
        # Multiple modifiers
        'c-s-f3', 'ctrl+shift+f3', 'control+shift+f3',
        'c-a-f3', 'ctrl+alt+f3', 'control+alt+f3',
        's-a-f3', 'shift+alt+f3', 'shift+meta+f3',
        'c-s-a-f3', 'ctrl+shift+alt+f3'
    ]
    
    # Try to add key bindings and track which ones succeed
    valid_combinations = []
    invalid_combinations = []
    
    for combo in key_combinations:
        try:
            @kb.add(combo)
            def _(event):
                pass
            valid_combinations.append(combo)
        except Exception as e:
            invalid_combinations.append((combo, str(e)))
    
    print("\nValid key combinations:")
    for combo in valid_combinations:
        print(f"  ✓ {combo}")
    
    print("\nInvalid key combinations:")
    for combo, error in invalid_combinations:
        print(f"  ✗ {combo}: {error}")

def test_shift_f3_specifically():
    """Focus specifically on finding the correct syntax for Shift+F3."""
    print("\n=== Specifically testing Shift+F3 combinations ===")
    
    kb = KeyBindings()
    
    # Try all possible variations for Shift+F3
    shift_f3_combinations = [
        'f3',  # Basic F3
        's-f3', 'S-f3',
        'shift+f3', 'Shift+f3', 'SHIFT+f3',
        'shift-f3', 'Shift-f3', 'SHIFT-f3',
        'shift f3', 'Shift f3', 'SHIFT f3',
        ('s', 'f3'), ('shift', 'f3'),
        Keys.F3, getattr(Keys, 'ShiftF3', None) if hasattr(Keys, 'ShiftF3') else None
    ]
    
    # Filter out None values
    shift_f3_combinations = [combo for combo in shift_f3_combinations if combo is not None]
    
    # Try to add key bindings and track which ones succeed
    valid_combinations = []
    invalid_combinations = []
    
    for combo in shift_f3_combinations:
        try:
            @kb.add(combo)
            def _(event):
                print(f"Shift+F3 pressed with combination: {combo}")
            valid_combinations.append(combo)
        except Exception as e:
            invalid_combinations.append((combo, str(e)))
    
    print("\nValid Shift+F3 combinations:")
    for combo in valid_combinations:
        print(f"  ✓ {combo}")
    
    print("\nInvalid Shift+F3 combinations:")
    for combo, error in invalid_combinations:
        print(f"  ✗ {combo}: {error}")

def create_test_application():
    """Create a small application to manually test key bindings."""
    print("\n=== Creating test application ===")
    print("Press any key to see its representation (Ctrl-C to exit)")
    
    kb = KeyBindings()
    
    @kb.add('c-c')
    def _(event):
        event.app.exit()
    
    # Default key binding to capture and display any pressed key
    @kb.add('any')
    def _(event):
        key_press = event.key_sequence[0]
        app.buffer = str(key_press)
    
    # Specifically try to catch Shift+F3 in different ways
    try:
        @kb.add('s-f3')
        def _(event):
            app.buffer = "Shift+F3 detected with 's-f3' format!"
    except Exception:
        pass
    
    try:
        @kb.add(Keys.F3, filter=lambda: is_shift_pressed())
        def _(event):
            app.buffer = "Shift+F3 detected with Keys.F3 + shift filter!"
    except Exception:
        # This is just for demonstration, is_shift_pressed is not implemented
        pass
    
    # Create a simple layout
    layout = Layout(Window(FormattedTextControl(lambda: app.buffer)))
    
    # Create the application
    app = Application(layout=layout, key_bindings=kb, full_screen=True)
    app.buffer = "Press any key to see its representation"
    
    print("Application created. Run with app.run() to test interactively.")
    return app

if __name__ == "__main__":
    print("prompt-toolkit Key Combinations Test\n")
    
    # Print all keys in the Keys enum
    print_all_keys_enum()
    
    # Test various key binding formats
    test_key_bindings()
    
    # Focus specifically on Shift+F3
    test_shift_f3_specifically()
    
    # Optionally, create an interactive test application
    # Uncomment to run the interactive test
    # app = create_test_application()
    # app.run()
    
    print("\nTest completed!")

