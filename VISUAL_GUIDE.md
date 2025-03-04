# TextShellEditor - Visual Guide

This document provides a visual representation of the TextShellEditor interface and its main features.

## Main Interface Layout

```
┌─────────────┬───────────────┬──────────────┬─────┐
│ 1: main.py* │ 2: utils.py   │ 3: [No File] │  +  │  <- Tab Bar
└─────────────┴───────────────┴──────────────┴─────┘
┌─ Editor ───────────────────────────────────────────┐
│ 1  def calculate_fibonacci(n):                     │
│ 2      """Calculate the Fibonacci sequence"""      │  <- Editor Area
│ 3      fib_sequence = [0, 1]                       │     (with syntax
│ 4                                                  │      highlighting)
│ 5      if n <= 2:                                  │
│ 6          return fib_sequence[:n]                 │
│ ...                                                │
└──────────────────────────────────────────────────┘
┌─ AI Code Insights ─────────────────────────────────┐
│ Function 'calculate_fibonacci' defined. It takes   │  <- AI Insights
│ 1 parameter. It includes a docstring.              │     Panel
└──────────────────────────────────────────────────┘
┌─ Terminal Output ─────────────────────────────────┐
│ $ python main.py                                   │
│ Calculating Fibonacci sequence for 10 terms:       │  <- Terminal
│ Term 1: 0                                          │     Output
│ ...                                                │
└──────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────┐
│ EDIT  main.py [+] [1/3]   AI analysis complete    │  <- Status Bar
└──────────────────────────────────────────────────┘
```

## Code Completion and Snippets

When typing code, pressing Ctrl+Space or typing trigger characters (like `.` for method completion) will display a completion popup:

```
for
┌─ Code Completion and Snippets ─────────────────────┐
│ > for: For loop                               📋   │
│   for_each: For each item in collection       📋   │
│   format                                           │
│   forward                                          │
└─────────────────────────────────────────────────────┘

# After selecting the snippet with TAB:
for item in items:
    pass

# The placeholders 'item' and 'items' are selected in turn
# as you press TAB to navigate through them
```

## Search and Replace

The search panel appears at the bottom when you press Ctrl+F:

```
┌─ Search ───────────────────────────────────────────┐
│ Find: fibonacci                                    │
│ [Next] [Prev] [Case sensitive]                     │
│ Replace: fib_calc                                  │
│ [Replace] [Replace All]                            │
└──────────────────────────────────────────────────┘
```

## Code Tooltips

Hovering over code elements or pressing Alt+H shows contextual tooltips:

```
def calculate_fibonacci(n):
    ┌───────────────────────────────────────┐
    │ Function with 1 parameter             │
    │ Calculates the Fibonacci sequence     │
    │ Returns a list of Fibonacci numbers   │
    └───────────────────────────────────────┘
    """Calculate the Fibonacci sequence up to n terms"""
```

## Features in Action

### Multi-tab Editing
- The tab bar shows all open files, with an asterisk (*) indicating unsaved changes
- Tabs are numbered for quick access with Alt+1, Alt+2, etc.
- The '+' button creates a new tab

### Interactive Terminal
- Execute commands directly in the terminal panel
- View command output without leaving the editor
- Execute the line under the cursor with Alt+Enter

### AI-Powered Insights
- Real-time code analysis shows insights about your code's structure
- Get suggestions for improvements and optimizations
- Toggle the insights panel with Ctrl+I

### Theme Support
- Choose from 5 built-in themes: default, monokai, solarized-dark, dracula, and one-dark
- Cycle themes with Alt+T to find your preferred style
- All themes work with the syntax highlighting system

### Code Folding
- Fold code blocks to focus on specific sections
- Toggle folding at cursor position with Alt+Z
- Visual indicators show where code is folded

### Syntax Checking
- Red underlines indicate syntax errors
- Hover over errors to see detailed error messages
- Real-time checking as you type (can be toggled with Alt+C)