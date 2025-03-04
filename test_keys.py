#!/usr/bin/env python3

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

def test_key_binding(key_combination, label):
    """Test if a key binding can be created with the given key combination."""
    kb = KeyBindings()
    try:
        @kb.add(key_combination)
        def _(event):
            print(f"{label} pressed: {key_combination}")
        print(f"✓ Successfully created binding for {label}: '{key_combination}'")
        return True
    except Exception as e:
        print(f"✗ Failed to create binding for {label}: '{key_combination}'")
        print(f"  Error: {e}")
        return False

# Test different formats for Shift+F3
print("\n=== Testing Shift+F3 Key Binding Formats ===\n")

formats = [
    ('s-f3', 'Standard s-f3'),
    ('shift+f3', 'Alternative shift+f3'),
    ('S-f3', 'Capital S-f3'),
    ('Shift+f3', 'Capital Shift+f3'),
    ('shift+F3', 'shift+capital F3'),
    ('Shift+F3', 'Capital Shift+capital F3'),
    (('s', 'f3'), 'Tuple (s, f3)'),
    (('shift', 'f3'), 'Tuple (shift, f3)'),
    ('f3', 'Just f3 for comparison')
]

successful_bindings = []

# Test each format
for key_format, label in formats:
    if test_key_binding(key_format, label):
        successful_bindings.append((key_format, label))

print("\n=== Summary of Successful Bindings ===\n")
if successful_bindings:
    for key_format, label in successful_bindings:
        print(f"✓ {label}: '{key_format}'")
else:
    print("No successful bindings found.")

print("\n=== Creating Function for Each Successful Binding ===\n")

# Create a function for each successful binding
kb = KeyBindings()
for key_format, label in successful_bindings:
    @kb.add(key_format)
    def _(event, key_format=key_format, label=label):
        print(f"Function triggered for {label}: '{key_format}'")

print("Key bindings have been created. In a real application, these would be triggered when the corresponding keys are pressed.")
print("To test them, you would need to run this in an interactive prompt-toolkit application.")

