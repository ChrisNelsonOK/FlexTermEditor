# TextShellEditor

A cutting-edge terminal-based text editor that transforms developer workflow through intelligent, interactive editing and shell integration.

## Overview

TextShellEditor is a Python-powered terminal application that combines a feature-rich text editor with an integrated shell, all enhanced with AI-powered code insights. It's designed for developers who prefer keyboard-centric workflows and want to maximize productivity without leaving the terminal.

![Editor Screenshot](VISUAL_GUIDE.md)

## Features

### 1. Multi-Tab Editing

- Tab-based interface for editing multiple files simultaneously
- Visual tab bar with file names and modification indicators
- Quick tab navigation with keyboard shortcuts
- Create, close, and switch between tabs without leaving the editor

### 2. Integrated Terminal

- Execute shell commands directly from the editor
- View command output in a dedicated panel
- Command history navigation
- Support for multiple shell types (bash, zsh, cmd)
- Execute the current line as a shell command with Alt+Enter

### 3. Syntax Highlighting and Code Quality

- Automatic language detection based on file extension
- Rich highlighting for a wide range of programming languages
- Support for Python, JavaScript, HTML, CSS, and many more
- Configurable color schemes
- Real-time syntax checking with error highlighting
- PEP 8 style checking for Python code
- Basic bracket/parenthesis matching for all languages

### 4. AI-Powered Code Insights

- Context-aware code analysis at cursor position
- Automatic detection of code constructs (functions, classes, loops, etc.)
- Intelligent insights about code structure and purpose
- Interactive code tooltips that provide contextual information
- Toggle insights panel with Ctrl+I
- Analyze code at cursor position with Alt+I
- Toggle code tooltips with Alt+H

### 5. Advanced Key Bindings

- Comprehensive keyboard shortcuts for all operations
- No need for mouse interaction
- Familiar key bindings similar to popular editors
- Help screen accessible via F1 key

### 6. Customizable Experience

- 5 built-in themes (default, monokai, solarized-dark, dracula, one-dark)
- Smart auto-indentation based on file type
- Toggle line wrapping (Alt+W)
- Toggle line numbers (Alt+N)
- Code folding for better navigation in large files

### 7. Search and Replace

- Find text with case-sensitive option
- Jump between search results with F3/Shift+F3
- Replace single or all matches 
- Toggle the search interface with Ctrl+F

### 8. Auto-Save

- Automatically saves files after a specified interval (default: 30 seconds)
- Can be toggled on/off with Alt+A
- Provides unobtrusive status notifications when saving
- Prevents data loss during unexpected shutdowns

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/text-shell-editor.git
cd text-shell-editor

# Install dependencies
pip install -r deploy_files/requirements.txt
```

### Dependencies

- Python 3.8+
- prompt_toolkit
- pygments
- pexpect
- pycodestyle

See [deploy_files/INSTALL.md](deploy_files/INSTALL.md) for detailed installation instructions.

## Web Deployment

TextShellEditor can be deployed as a web application using Docker:

```bash
# Quick start with Docker Compose
docker-compose -f deploy_files/docker-compose.yml up -d

# Or build and run the Docker image manually
docker build -f deploy_files/Dockerfile -t textshell-editor .
docker run -p 8080:8080 textshell-editor
```

Access the editor at http://localhost:8080

## Usage

```bash
# Basic usage
python text_shell_editor.py [filename]

# Specify a shell to use
python text_shell_editor.py --shell bash myfile.py

# View demo mode (for restricted terminal environments)
python text_shell_editor.py --demo
```

## Keyboard Shortcuts

### General
- Ctrl+Q: Exit the application
- Ctrl+S: Save the current file
- F1: Show help screen

### Tab Management
- Ctrl+N: Create a new tab
- Ctrl+W: Close the current tab
- Ctrl+Right: Switch to the next tab
- Ctrl+Left: Switch to the previous tab
- Alt+1...9: Switch to a specific tab by number

### Terminal Control
- Alt+Enter: Execute the current line as a shell command
- Ctrl+T: Toggle terminal visibility
- Ctrl+L: Clear the terminal output
- Ctrl+B: Cycle through available shells

### AI Features
- Ctrl+I: Toggle AI code insights panel
- Alt+I: Analyze code at current cursor position
- Alt+H: Toggle code insight tooltips

### View Options
- Alt+W: Toggle line wrapping
- Alt+N: Toggle line numbers
- Alt+A: Toggle auto-save feature
- Alt+F: Toggle code folding
- Alt+Z: Toggle fold at cursor position

### Search and Replace
- Ctrl+F: Toggle search & replace panel
- F3: Find next match
- Shift+F3: Find previous match

## Terminal Requirements

For the best experience, use a terminal with:
- A minimum size of 80x24 characters
- Support for 256 colors
- A monospaced font

## Demo Mode

If your terminal doesn't meet the minimum size requirements, or if you use the `--demo` flag, TextShellEditor will display information about its features instead of launching the interactive interface.

For a visual representation of what the UI looks like, see [VISUAL_GUIDE.md](VISUAL_GUIDE.md).

## Development Notes

### Language Server Protocol (LSP) Warnings

When developing the application, you may notice LSP warnings in your editor related to missing imports from the `prompt_toolkit` library and other dependencies. These warnings are expected since LSP may not resolve the imports correctly, but the application will function properly as long as the dependencies are installed.

The warnings typically look like:
```
Import "prompt_toolkit" could not be resolved
Import "prompt_toolkit.layout" could not be resolved
```

These can be safely ignored as the imports will resolve correctly at runtime when the proper dependencies are installed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) for the powerful terminal UI framework
- [pygments](https://pygments.org/) for syntax highlighting
- [pexpect](https://pexpect.readthedocs.io/) for terminal interaction