#!/usr/bin/env python3
"""
Theme Management - Handles customizable editor themes
"""

import re
from prompt_toolkit.styles import Style

# Define theme presets
THEMES = {
    "default": {
        # Status bar styles
        'status-bar': 'bg:#333333 #ffffff',
        'status-bar.mode': 'bg:#9a12b3 #ffffff bold',
        'status-bar.shell': 'bg:#666666 #ffffff',
        'status-bar.filename': 'bg:#333333 #ffffff',
        'status-bar.info': '#00ff00',
        'status-bar.warning': '#ffff00',
        'status-bar.error': '#ff0000',
        
        # Tab bar styles
        'tab-bar': 'bg:#222222',
        'tab': 'bg:#444444 #ffffff',
        'tab.active': 'bg:#0066cc #ffffff bold',
        'tab.new': 'bg:#226622 #ffffff',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#550000 #ffffff',
        
        # Search result highlighting
        'search-result': 'bg:#304060 #ffffff',
        'search-result.current': 'bg:#605030 #ffffff bold',
        
        # Code completion styling
        'completion-popup': 'bg:#223344 #aaddff',
        'completion-popup.selection': 'bg:#3a5998 #ffffff bold',
        
        # Editor styles
        'line-number': '#aaaaaa',
        'cursor-line': 'bg:#3a3d41',
        
        # Terminal styles
        'terminal': '#00ff00 bg:#000000',
        'command-output': '#aaaaff',
        'command-error': '#ff5555',
        'info-message': '#00aa00',
        'warning-message': '#aaaa00',
        'error-message': '#aa0000',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#102030',
        'insight.analyzing': 'bg:#2a2a40 #ffaa00 italic',
        'insight.content': 'bg:#102030 #00ddff',
        'insight.empty': 'bg:#102030 #666666 italic',
        'insight.suggestion': 'bg:#102030 #00ff00',  # Green for suggestions
        'insight.warning': 'bg:#102030 #ffaa00',  # Amber for warnings
        'insight.tip': 'bg:#102030 #aaaaaa italic',  # Gray for tips
        'insight-tooltip': 'bg:#223344 #00eeff',  # Tooltip background and text
        
        # Code analysis styles
        'folded-code': '#888888 italic',
    },
    
    "monokai": {
        # Status bar styles
        'status-bar': 'bg:#272822 #f8f8f2',
        'status-bar.mode': 'bg:#f92672 #f8f8f2 bold',
        'status-bar.shell': 'bg:#383830 #f8f8f2',
        'status-bar.filename': 'bg:#272822 #f8f8f2',
        'status-bar.info': '#a6e22e',
        'status-bar.warning': '#e6db74',
        'status-bar.error': '#f92672',
        
        # Tab bar styles
        'tab-bar': 'bg:#1e1f1c',
        'tab': 'bg:#383830 #f8f8f2',
        'tab.active': 'bg:#f92672 #f8f8f2 bold',
        'tab.new': 'bg:#a6e22e #272822',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#4a161c #f8f8f2',
        
        # Search result highlighting
        'search-result': 'bg:#3e5c80 #f8f8f2',
        'search-result.current': 'bg:#a6772e #f8f8f2 bold',
        
        # Code completion styling
        'completion-popup': 'bg:#272822 #66d9ef',
        'completion-popup.selection': 'bg:#a6e22e #272822 bold',
        
        # Editor styles
        'line-number': '#75715e',
        'cursor-line': 'bg:#3e3d32',
        
        # Terminal styles
        'terminal': '#a6e22e bg:#272822',
        'command-output': '#66d9ef',
        'command-error': '#f92672',
        'info-message': '#a6e22e',
        'warning-message': '#e6db74',
        'error-message': '#f92672',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#232425',
        'insight.analyzing': 'bg:#3e3d32 #e6db74 italic',
        'insight.content': 'bg:#232425 #66d9ef',
        'insight.empty': 'bg:#232425 #75715e italic',
        'insight.suggestion': 'bg:#232425 #a6e22e',  # Green for suggestions
        'insight.warning': 'bg:#232425 #e6db74',  # Yellow for warnings
        'insight.tip': 'bg:#232425 #75715e italic',  # Gray for tips
        'insight-tooltip': 'bg:#272822 #66d9ef',  # Tooltip background and text
    },
    
    "solarized-dark": {
        # Status bar styles
        'status-bar': 'bg:#002b36 #93a1a1',
        'status-bar.mode': 'bg:#cb4b16 #fdf6e3 bold',
        'status-bar.shell': 'bg:#073642 #93a1a1',
        'status-bar.filename': 'bg:#002b36 #93a1a1',
        'status-bar.info': '#859900',
        'status-bar.warning': '#b58900',
        'status-bar.error': '#dc322f',
        
        # Tab bar styles
        'tab-bar': 'bg:#001e26',
        'tab': 'bg:#073642 #93a1a1',
        'tab.active': 'bg:#268bd2 #fdf6e3 bold',
        'tab.new': 'bg:#859900 #002b36',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#8c2d23 #fdf6e3',
        
        # Editor styles
        'line-number': '#657b83',
        'cursor-line': 'bg:#073642',
        
        # Terminal styles
        'terminal': '#859900 bg:#002b36',
        'command-output': '#2aa198',
        'command-error': '#dc322f',
        'info-message': '#859900',
        'warning-message': '#b58900',
        'error-message': '#dc322f',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#00212b',
        'insight.analyzing': 'bg:#073642 #b58900 italic',
        'insight.content': 'bg:#00212b #2aa198',
        'insight.empty': 'bg:#00212b #657b83 italic',
    },
    
    "dracula": {
        # Status bar styles
        'status-bar': 'bg:#282a36 #f8f8f2',
        'status-bar.mode': 'bg:#ff79c6 #f8f8f2 bold',
        'status-bar.shell': 'bg:#44475a #f8f8f2',
        'status-bar.filename': 'bg:#282a36 #f8f8f2',
        'status-bar.info': '#50fa7b',
        'status-bar.warning': '#f1fa8c',
        'status-bar.error': '#ff5555',
        
        # Tab bar styles
        'tab-bar': 'bg:#21222c',
        'tab': 'bg:#44475a #f8f8f2',
        'tab.active': 'bg:#bd93f9 #f8f8f2 bold',
        'tab.new': 'bg:#50fa7b #282a36',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#642530 #f8f8f2',
        
        # Search result highlighting
        'search-result': 'bg:#4d5b8c #f8f8f2',
        'search-result.current': 'bg:#8c6a54 #f8f8f2 bold',
        
        # Code completion styling
        'completion-popup': 'bg:#282a36 #8be9fd',
        'completion-popup.selection': 'bg:#bd93f9 #f8f8f2 bold',
        
        # Editor styles
        'line-number': '#6272a4',
        'cursor-line': 'bg:#44475a',
        
        # Terminal styles
        'terminal': '#50fa7b bg:#282a36',
        'command-output': '#8be9fd',
        'command-error': '#ff5555',
        'info-message': '#50fa7b',
        'warning-message': '#f1fa8c',
        'error-message': '#ff5555',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#1e1f29',
        'insight.analyzing': 'bg:#44475a #f1fa8c italic',
        'insight.content': 'bg:#1e1f29 #8be9fd',
        'insight.empty': 'bg:#1e1f29 #6272a4 italic',
        'insight.suggestion': 'bg:#1e1f29 #50fa7b',  # Green for suggestions
        'insight.warning': 'bg:#1e1f29 #f1fa8c',  # Yellow for warnings
        'insight.tip': 'bg:#1e1f29 #6272a4 italic',  # Gray for tips
        'insight-tooltip': 'bg:#282a36 #8be9fd',  # Tooltip background and text
    },
    
    "one-dark": {
        # Status bar styles
        'status-bar': 'bg:#282c34 #abb2bf',
        'status-bar.mode': 'bg:#c678dd #ffffff bold',
        'status-bar.shell': 'bg:#3e4451 #abb2bf',
        'status-bar.filename': 'bg:#282c34 #abb2bf',
        'status-bar.info': '#98c379',
        'status-bar.warning': '#e5c07b',
        'status-bar.error': '#e06c75',
        
        # Tab bar styles
        'tab-bar': 'bg:#21252b',
        'tab': 'bg:#3e4451 #abb2bf',
        'tab.active': 'bg:#61afef #ffffff bold',
        'tab.new': 'bg:#98c379 #282c34',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#53232e #abb2bf',
        
        # Search result highlighting
        'search-result': 'bg:#2c4d80 #abb2bf',
        'search-result.current': 'bg:#7c6119 #abb2bf bold',
        
        # Code completion styling
        'completion-popup': 'bg:#282c34 #56b6c2',
        'completion-popup.selection': 'bg:#61afef #ffffff bold',
        
        # Editor styles
        'line-number': '#636d83',
        'cursor-line': 'bg:#2c313a',
        
        # Terminal styles
        'terminal': '#98c379 bg:#282c34',
        'command-output': '#56b6c2',
        'command-error': '#e06c75',
        'info-message': '#98c379',
        'warning-message': '#e5c07b',
        'error-message': '#e06c75',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#1f2329',
        'insight.analyzing': 'bg:#3e4451 #e5c07b italic',
        'insight.content': 'bg:#1f2329 #56b6c2',
        'insight.empty': 'bg:#1f2329 #636d83 italic',
        'insight.suggestion': 'bg:#1f2329 #98c379',  # Green for suggestions
        'insight.warning': 'bg:#1f2329 #e5c07b',  # Yellow for warnings
        'insight.tip': 'bg:#1f2329 #636d83 italic',  # Gray for tips
        'insight-tooltip': 'bg:#282c34 #56b6c2',  # Tooltip background and text
    },
    
    "nord": {
        # Status bar styles
        'status-bar': 'bg:#2e3440 #d8dee9',
        'status-bar.mode': 'bg:#5e81ac #eceff4 bold',
        'status-bar.shell': 'bg:#3b4252 #d8dee9',
        'status-bar.filename': 'bg:#2e3440 #d8dee9',
        'status-bar.info': '#a3be8c',
        'status-bar.warning': '#ebcb8b',
        'status-bar.error': '#bf616a',
        
        # Tab bar styles
        'tab-bar': 'bg:#272c36',
        'tab': 'bg:#3b4252 #d8dee9',
        'tab.active': 'bg:#88c0d0 #2e3440 bold',
        'tab.new': 'bg:#a3be8c #2e3440',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#4c2f35 #d8dee9',
        
        # Editor styles
        'line-number': '#4c566a',
        'cursor-line': 'bg:#3b4252',
        
        # Terminal styles
        'terminal': '#a3be8c bg:#2e3440',
        'command-output': '#88c0d0',
        'command-error': '#bf616a',
        'info-message': '#a3be8c',
        'warning-message': '#ebcb8b',
        'error-message': '#bf616a',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#242933',
        'insight.analyzing': 'bg:#3b4252 #ebcb8b italic',
        'insight.content': 'bg:#242933 #88c0d0',
        'insight.empty': 'bg:#242933 #4c566a italic',
        'insight.suggestion': 'bg:#242933 #a3be8c',  # Green for suggestions
        'insight.warning': 'bg:#242933 #ebcb8b',  # Yellow for warnings
        'insight.tip': 'bg:#242933 #4c566a italic',  # Gray for tips
        'insight-tooltip': 'bg:#2e3440 #88c0d0',  # Tooltip background and text
    },
    
    "github-dark": {
        # Status bar styles
        'status-bar': 'bg:#0d1117 #c9d1d9',
        'status-bar.mode': 'bg:#1f6feb #ffffff bold',
        'status-bar.shell': 'bg:#161b22 #c9d1d9',
        'status-bar.filename': 'bg:#0d1117 #c9d1d9',
        'status-bar.info': '#7ee787',
        'status-bar.warning': '#f2cc60',
        'status-bar.error': '#f85149',
        
        # Tab bar styles
        'tab-bar': 'bg:#090c10',
        'tab': 'bg:#161b22 #c9d1d9',
        'tab.active': 'bg:#1f6feb #ffffff bold',
        'tab.new': 'bg:#238636 #ffffff',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#5d1a18 #f0f6fc',
        
        # Editor styles
        'line-number': '#8b949e',
        'cursor-line': 'bg:#161b22',
        
        # Terminal styles
        'terminal': '#7ee787 bg:#0d1117',
        'command-output': '#58a6ff',
        'command-error': '#f85149',
        'info-message': '#7ee787',
        'warning-message': '#f2cc60',
        'error-message': '#f85149',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#0a0d13',
        'insight.analyzing': 'bg:#161b22 #f2cc60 italic',
        'insight.content': 'bg:#0a0d13 #58a6ff',
        'insight.empty': 'bg:#0a0d13 #8b949e italic',
        'insight.suggestion': 'bg:#0a0d13 #7ee787',  # Green for suggestions
        'insight.warning': 'bg:#0a0d13 #f2cc60',  # Yellow for warnings
        'insight.tip': 'bg:#0a0d13 #8b949e italic',  # Gray for tips
        'insight-tooltip': 'bg:#0d1117 #58a6ff',  # Tooltip background and text
    },
    
    "github-light": {
        # Status bar styles
        'status-bar': 'bg:#ffffff #24292f',
        'status-bar.mode': 'bg:#0969da #ffffff bold',
        'status-bar.shell': 'bg:#f6f8fa #24292f',
        'status-bar.filename': 'bg:#ffffff #24292f',
        'status-bar.info': '#1a7f37',
        'status-bar.warning': '#9a6700',
        'status-bar.error': '#cf222e',
        
        # Tab bar styles
        'tab-bar': 'bg:#f6f8fa',
        'tab': 'bg:#eaeef2 #24292f',
        'tab.active': 'bg:#0969da #ffffff bold',
        'tab.new': 'bg:#1a7f37 #ffffff',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#ffebe9 #24292f',
        
        # Editor styles
        'line-number': '#6e7781',
        'cursor-line': 'bg:#f6f8fa',
        
        # Terminal styles
        'terminal': '#1a7f37 bg:#ffffff',
        'command-output': '#0550ae',
        'command-error': '#cf222e',
        'info-message': '#1a7f37',
        'warning-message': '#9a6700',
        'error-message': '#cf222e',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#f6f8fa',
        'insight.analyzing': 'bg:#eaeef2 #9a6700 italic',
        'insight.content': 'bg:#f6f8fa #0550ae',
        'insight.empty': 'bg:#f6f8fa #6e7781 italic',
        'insight.suggestion': 'bg:#f6f8fa #1a7f37',  # Green for suggestions
        'insight.warning': 'bg:#f6f8fa #9a6700',  # Yellow for warnings
        'insight.tip': 'bg:#f6f8fa #6e7781 italic',  # Gray for tips
        'insight-tooltip': 'bg:#ffffff #0550ae',  # Tooltip background and text
    },
    
    "material": {
        # Status bar styles
        'status-bar': 'bg:#263238 #eeffff',
        'status-bar.mode': 'bg:#c792ea #ffffff bold',
        'status-bar.shell': 'bg:#37474f #eeffff',
        'status-bar.filename': 'bg:#263238 #eeffff',
        'status-bar.info': '#c3e88d',
        'status-bar.warning': '#ffcb6b',
        'status-bar.error': '#f07178',
        
        # Tab bar styles
        'tab-bar': 'bg:#1c2529',
        'tab': 'bg:#37474f #eeffff',
        'tab.active': 'bg:#82aaff #ffffff bold',
        'tab.new': 'bg:#c3e88d #263238',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#5c2d32 #eeffff',
        
        # Editor styles
        'line-number': '#546e7a',
        'cursor-line': 'bg:#303c41',
        
        # Terminal styles
        'terminal': '#c3e88d bg:#263238',
        'command-output': '#89ddff',
        'command-error': '#f07178',
        'info-message': '#c3e88d',
        'warning-message': '#ffcb6b',
        'error-message': '#f07178',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#1a2327',
        'insight.analyzing': 'bg:#37474f #ffcb6b italic',
        'insight.content': 'bg:#1a2327 #89ddff',
        'insight.empty': 'bg:#1a2327 #546e7a italic',
        'insight.suggestion': 'bg:#1a2327 #c3e88d',  # Green for suggestions
        'insight.warning': 'bg:#1a2327 #ffcb6b',  # Yellow for warnings
        'insight.tip': 'bg:#1a2327 #546e7a italic',  # Gray for tips
        'insight-tooltip': 'bg:#263238 #89ddff',  # Tooltip background and text
    },
    
    "gruvbox": {
        # Status bar styles
        'status-bar': 'bg:#282828 #ebdbb2',
        'status-bar.mode': 'bg:#d3869b #fbf1c7 bold',
        'status-bar.shell': 'bg:#3c3836 #ebdbb2',
        'status-bar.filename': 'bg:#282828 #ebdbb2',
        'status-bar.info': '#b8bb26',
        'status-bar.warning': '#fabd2f',
        'status-bar.error': '#fb4934',
        
        # Tab bar styles
        'tab-bar': 'bg:#1d2021',
        'tab': 'bg:#3c3836 #ebdbb2',
        'tab.active': 'bg:#458588 #fbf1c7 bold',
        'tab.new': 'bg:#98971a #fbf1c7',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#4c2521 #ebdbb2',
        
        # Editor styles
        'line-number': '#7c6f64',
        'cursor-line': 'bg:#32302f',
        
        # Terminal styles
        'terminal': '#b8bb26 bg:#282828',
        'command-output': '#83a598',
        'command-error': '#fb4934',
        'info-message': '#b8bb26',
        'warning-message': '#fabd2f',
        'error-message': '#fb4934',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#1d2021',
        'insight.analyzing': 'bg:#3c3836 #fabd2f italic',
        'insight.content': 'bg:#1d2021 #83a598',
        'insight.empty': 'bg:#1d2021 #7c6f64 italic',
        'insight.suggestion': 'bg:#1d2021 #b8bb26',  # Green for suggestions
        'insight.warning': 'bg:#1d2021 #fabd2f',  # Yellow for warnings
        'insight.tip': 'bg:#1d2021 #7c6f64 italic',  # Gray for tips
        'insight-tooltip': 'bg:#282828 #83a598',  # Tooltip background and text
    },
    
    "tokyo-night": {
        # Status bar styles
        'status-bar': 'bg:#1a1b26 #c0caf5',
        'status-bar.mode': 'bg:#bb9af7 #1a1b26 bold',
        'status-bar.shell': 'bg:#24283b #c0caf5',
        'status-bar.filename': 'bg:#1a1b26 #c0caf5',
        'status-bar.info': '#9ece6a',
        'status-bar.warning': '#e0af68',
        'status-bar.error': '#f7768e',
        
        # Tab bar styles
        'tab-bar': 'bg:#16161e',
        'tab': 'bg:#24283b #c0caf5',
        'tab.active': 'bg:#7aa2f7 #1a1b26 bold',
        'tab.new': 'bg:#9ece6a #1a1b26',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#3b2532 #c0caf5',
        
        # Editor styles
        'line-number': '#565f89',
        'cursor-line': 'bg:#292e42',
        
        # Terminal styles
        'terminal': '#9ece6a bg:#1a1b26',
        'command-output': '#7dcfff',
        'command-error': '#f7768e',
        'info-message': '#9ece6a',
        'warning-message': '#e0af68',
        'error-message': '#f7768e',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#16161e',
        'insight.analyzing': 'bg:#24283b #e0af68 italic',
        'insight.content': 'bg:#16161e #7dcfff',
        'insight.empty': 'bg:#16161e #565f89 italic',
        'insight.suggestion': 'bg:#16161e #9ece6a',  # Green for suggestions
        'insight.warning': 'bg:#16161e #e0af68',  # Yellow for warnings
        'insight.tip': 'bg:#16161e #565f89 italic',  # Gray for tips
        'insight-tooltip': 'bg:#1a1b26 #7dcfff',  # Tooltip background and text
    },
    
    "catppuccin": {
        # Status bar styles
        'status-bar': 'bg:#1e1e2e #cdd6f4',
        'status-bar.mode': 'bg:#cba6f7 #1e1e2e bold',
        'status-bar.shell': 'bg:#313244 #cdd6f4',
        'status-bar.filename': 'bg:#1e1e2e #cdd6f4',
        'status-bar.info': '#a6e3a1',
        'status-bar.warning': '#f9e2af',
        'status-bar.error': '#f38ba8',
        
        # Tab bar styles
        'tab-bar': 'bg:#181825',
        'tab': 'bg:#313244 #cdd6f4',
        'tab.active': 'bg:#89b4fa #1e1e2e bold',
        'tab.new': 'bg:#a6e3a1 #1e1e2e',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#362839 #cdd6f4',
        
        # Editor styles
        'line-number': '#585b70',
        'cursor-line': 'bg:#313244',
        
        # Terminal styles
        'terminal': '#a6e3a1 bg:#1e1e2e',
        'command-output': '#89dceb',
        'command-error': '#f38ba8',
        'info-message': '#a6e3a1',
        'warning-message': '#f9e2af',
        'error-message': '#f38ba8',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#181825',
        'insight.analyzing': 'bg:#313244 #f9e2af italic',
        'insight.content': 'bg:#181825 #89dceb',
        'insight.empty': 'bg:#181825 #585b70 italic',
        'insight.suggestion': 'bg:#181825 #a6e3a1',  # Green for suggestions
        'insight.warning': 'bg:#181825 #f9e2af',  # Yellow for warnings
        'insight.tip': 'bg:#181825 #585b70 italic',  # Gray for tips
        'insight-tooltip': 'bg:#1e1e2e #89dceb',  # Tooltip background and text
    },
    
    "everforest": {
        # Status bar styles
        'status-bar': 'bg:#2d353b #d3c6aa',
        'status-bar.mode': 'bg:#d699b6 #2d353b bold',
        'status-bar.shell': 'bg:#3a464c #d3c6aa',
        'status-bar.filename': 'bg:#2d353b #d3c6aa',
        'status-bar.info': '#a7c080',
        'status-bar.warning': '#dbbc7f',
        'status-bar.error': '#e67e80',
        
        # Tab bar styles
        'tab-bar': 'bg:#272e33',
        'tab': 'bg:#3a464c #d3c6aa',
        'tab.active': 'bg:#7fbbb3 #2d353b bold',
        'tab.new': 'bg:#a7c080 #2d353b',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#4c3232 #d3c6aa',
        
        # Editor styles
        'line-number': '#859289',
        'cursor-line': 'bg:#343f44',
        
        # Terminal styles
        'terminal': '#a7c080 bg:#2d353b',
        'command-output': '#7fbbb3',
        'command-error': '#e67e80',
        'info-message': '#a7c080',
        'warning-message': '#dbbc7f',
        'error-message': '#e67e80',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#272e33',
        'insight.analyzing': 'bg:#3a464c #dbbc7f italic',
        'insight.content': 'bg:#272e33 #7fbbb3',
        'insight.empty': 'bg:#272e33 #859289 italic',
        'insight.suggestion': 'bg:#272e33 #a7c080',  # Green for suggestions
        'insight.warning': 'bg:#272e33 #dbbc7f',  # Yellow for warnings 
        'insight.tip': 'bg:#272e33 #859289 italic',  # Gray for tips
        'insight-tooltip': 'bg:#2d353b #7fbbb3',  # Tooltip background and text
    },
    
    "cyberpunk": {
        # Status bar styles
        'status-bar': 'bg:#120458 #00ffff',
        'status-bar.mode': 'bg:#ff00ff #120458 bold',
        'status-bar.shell': 'bg:#221c77 #00ffff',
        'status-bar.filename': 'bg:#120458 #00ffff',
        'status-bar.info': '#00ff84',
        'status-bar.warning': '#ffcc00',
        'status-bar.error': '#ff0055',
        
        # Tab bar styles
        'tab-bar': 'bg:#0b0335',
        'tab': 'bg:#221c77 #00ffff',
        'tab.active': 'bg:#00a2ff #120458 bold',
        'tab.new': 'bg:#00ff84 #120458',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#550033 #00ffff',
        
        # Editor styles
        'line-number': '#6845ff',
        'cursor-line': 'bg:#1a0f6b',
        
        # Terminal styles
        'terminal': '#00ff84 bg:#120458',
        'command-output': '#00ffff',
        'command-error': '#ff0055',
        'info-message': '#00ff84',
        'warning-message': '#ffcc00',
        'error-message': '#ff0055',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#0b0335',
        'insight.analyzing': 'bg:#221c77 #ffcc00 italic',
        'insight.content': 'bg:#0b0335 #00ffff',
        'insight.empty': 'bg:#0b0335 #6845ff italic',
        'insight.suggestion': 'bg:#0b0335 #00ff84',  # Green for suggestions
        'insight.warning': 'bg:#0b0335 #ffcc00',  # Yellow for warnings
        'insight.tip': 'bg:#0b0335 #6845ff italic',  # Purple for tips
        'insight-tooltip': 'bg:#120458 #00ffff',  # Tooltip background and text
    },
    
    "synthwave": {
        # Status bar styles
        'status-bar': 'bg:#262335 #ff7edb',
        'status-bar.mode': 'bg:#b893ce #262335 bold',
        'status-bar.shell': 'bg:#34294f #ff7edb',
        'status-bar.filename': 'bg:#262335 #ff7edb',
        'status-bar.info': '#72f1b8',
        'status-bar.warning': '#fede5d',
        'status-bar.error': '#fe4450',
        
        # Tab bar styles
        'tab-bar': 'bg:#1a1628',
        'tab': 'bg:#34294f #ff7edb',
        'tab.active': 'bg:#36f9f6 #262335 bold',
        'tab.new': 'bg:#72f1b8 #262335',
        
        # Syntax error highlighting
        'syntax-error': 'bg:#471a27 #ff7edb',
        
        # Editor styles
        'line-number': '#848bbd',
        'cursor-line': 'bg:#34294f',
        
        # Terminal styles
        'terminal': '#72f1b8 bg:#262335',
        'command-output': '#36f9f6',
        'command-error': '#fe4450',
        'info-message': '#72f1b8',
        'warning-message': '#fede5d',
        'error-message': '#fe4450',
        
        # AI Insights panel styles
        'insight-panel': 'bg:#1a1628',
        'insight.analyzing': 'bg:#34294f #fede5d italic',
        'insight.content': 'bg:#1a1628 #36f9f6',
        'insight.empty': 'bg:#1a1628 #848bbd italic',
        'insight.suggestion': 'bg:#1a1628 #72f1b8',  # Green for suggestions
        'insight.warning': 'bg:#1a1628 #fede5d',  # Yellow for warnings
        'insight.tip': 'bg:#1a1628 #848bbd italic',  # Gray for tips
        'insight-tooltip': 'bg:#262335 #36f9f6',  # Tooltip background and text
    },
}

def get_available_themes():
    """Return a list of all available theme names
    
    Returns:
        list: List of theme names as strings
    """
    return list(THEMES.keys())

def get_theme_style(theme_name="default"):
    """Get Style object for the specified theme"""
    # Make sure theme_name is a string
    if not isinstance(theme_name, str):
        print(f"Invalid theme name type. Using default theme.")
        theme_name = "default"
    
    if theme_name not in THEMES:
        print(f"Theme '{theme_name}' not found. Using default theme.")
        theme_name = "default"
    
    return Style.from_dict(THEMES[theme_name])

def preview_theme(theme_name):
    """Generate a textual preview of the theme"""
    if theme_name not in THEMES:
        print(f"Theme '{theme_name}' not found.")
        return
        
    theme = THEMES[theme_name]
    
    print(f"\nTheme Preview: {theme_name}\n")
    print("=" * 50)
    
    # Extract common background colors for demonstration
    main_bg = None
    for key in ['status-bar', 'tab-bar', 'terminal']:
        if key in theme:
            style = theme[key]
            bg_match = re.search(r'bg:(#[0-9a-fA-F]{6})', style)
            if bg_match:
                main_bg = bg_match.group(1)
                break
    
    if not main_bg:
        main_bg = "#000000"  # Default to black if no background found
    
    # Create a simulated UI display
    ui_width = 50
    
    # Simulate a tab bar
    tab_bar_bg = extract_color(theme.get('tab-bar', 'bg:#222222'), 'bg')
    tab_bg = extract_color(theme.get('tab', 'bg:#444444'), 'bg')
    tab_fg = extract_color(theme.get('tab', '#ffffff'), 'fg')
    active_tab_bg = extract_color(theme.get('tab.active', 'bg:#0066cc'), 'bg')
    active_tab_fg = extract_color(theme.get('tab.active', '#ffffff'), 'fg')
    
    print(f"┌{'─' * (ui_width-2)}┐")
    print(f"│ {colorize('Tab Bar Background', tab_bar_bg, tab_bar_bg, pad_to=ui_width-4)} │")
    print(f"│ {colorize('  Tab 1  ', active_tab_bg, active_tab_fg, pad_to=10)} {colorize('  Tab 2  ', tab_bg, tab_fg, pad_to=10)} {colorize('  + New  ', extract_color(theme.get('tab.new', 'bg:#226622'), 'bg'), extract_color(theme.get('tab.new', '#ffffff'), 'fg'), pad_to=10)} {' ' * (ui_width-36)} │")
    
    # Simulate editor area
    editor_bg = extract_color(theme.get('cursor-line', 'bg:#3a3d41'), 'bg').replace('bg:', '')
    
    print(f"│ {colorize(' Editor Area', editor_bg, '#ffffff', pad_to=ui_width-4)} │")
    print(f"│ {colorize(' 1 def example():', editor_bg, '#ffffff', pad_to=ui_width-4)} │")
    print(f"│ {colorize(' 2     # This is a comment', editor_bg, '#888888', pad_to=ui_width-4)} │")
    print(f"│ {colorize(' 3     value = calculate()', editor_bg, '#ffffff', pad_to=ui_width-4)} │")
    print(f"│ {colorize(' 4     if value > 10:', editor_bg, '#ffffff', pad_to=ui_width-4)} │")
    content = colorize(' 5         print("Error message")', editor_bg, '#ffffff', pad_to=ui_width-4)
    print("│ " + content + " │")
    
    # Simulate error highlighting
    error_bg = extract_color(theme.get('syntax-error', 'bg:#550000'), 'bg').replace('bg:', '')
    print(f"│ {colorize(' 6     reutrn value  # Syntax error', error_bg, '#ffffff', pad_to=ui_width-4)} │")
    
    # Simulate terminal
    terminal_bg = extract_color(theme.get('terminal', 'bg:#000000'), 'bg').replace('bg:', '')
    terminal_fg = extract_color(theme.get('terminal', '#00ff00'), 'fg')
    
    print(f"├{'─' * (ui_width-2)}┤")
    print(f"│ {colorize(' Terminal', terminal_bg, terminal_fg, pad_to=ui_width-4)} │")
    print(f"│ {colorize(' $ python example.py', terminal_bg, terminal_fg, pad_to=ui_width-4)} │")
    
    # Command output
    output_color = extract_color(theme.get('command-output', '#aaaaff'), 'fg')
    print(f"│ {colorize(' Processing data...', terminal_bg, output_color, pad_to=ui_width-4)} │")
    
    # Error message
    error_color = extract_color(theme.get('command-error', '#ff5555'), 'fg')
    print(f"│ {colorize(' Error: Invalid syntax on line 6', terminal_bg, error_color, pad_to=ui_width-4)} │")
    
    # Status bar
    status_bar_bg = extract_color(theme.get('status-bar', 'bg:#333333'), 'bg').replace('bg:', '')
    status_bar_fg = extract_color(theme.get('status-bar', '#ffffff'), 'fg')
    mode_bg = extract_color(theme.get('status-bar.mode', 'bg:#9a12b3'), 'bg').replace('bg:', '')
    mode_fg = extract_color(theme.get('status-bar.mode', '#ffffff'), 'fg')
    
    print(f"├{'─' * (ui_width-2)}┤")
    print(f"│ {colorize(' NORMAL ', mode_bg, mode_fg, pad_to=10)}{colorize(' example.py ', status_bar_bg, status_bar_fg, pad_to=ui_width-14)} │")
    print(f"└{'─' * (ui_width-2)}┘")
    
    print("\nDetailed Color Information:")
    print("=" * 50)
    
    # Preview categories with detailed information
    categories = [
        ("Status Bar", ["status-bar", "status-bar.mode", "status-bar.filename"]),
        ("Tab Bar", ["tab-bar", "tab", "tab.active", "tab.new"]),
        ("Editor", ["line-number", "cursor-line", "syntax-error"]),
        ("Terminal", ["terminal", "command-output", "command-error"]),
        ("Messages", ["info-message", "warning-message", "error-message"]),
        ("AI Insights", ["insight-panel", "insight.analyzing", "insight.content", "insight.empty", 
                        "insight.suggestion", "insight.warning", "insight.tip", "insight-tooltip"]),
    ]
    
    for category_name, elements in categories:
        print(f"\n{category_name}:")
        for element in elements:
            if element in theme:
                print(f"  - {element}: {theme[element]}")

def extract_color(style, type_):
    """Extract background or foreground color from a style string
    
    Args:
        style: Style string like 'bg:#123456 #abcdef'
        type_: Either 'bg' for background or 'fg' for foreground
        
    Returns:
        Extracted color with prefix (for bg) or just the color (for fg)
    """
    if not style:
        return '#ffffff' if type_ == 'fg' else 'bg:#000000'
        
    if type_ == 'bg':
        match = re.search(r'bg:(#[0-9a-fA-F]{6})', style)
        if match:
            return match.group(0)  # Return with 'bg:' prefix
        return 'bg:#000000'  # Default background
    else:  # fg
        # First check for standalone color
        match = re.search(r'(?<!\w)(#[0-9a-fA-F]{6})(?!\w)', style)
        if match:
            return match.group(1)
        # Then check if there's any color that's not a background
        match = re.search(r'(?<!bg:)(#[0-9a-fA-F]{6})', style)
        if match:
            return match.group(1)
        return '#ffffff'  # Default foreground

def colorize(text, bg_color, fg_color, pad_to=None):
    """Create a colorized text representation
    
    Args:
        text: The text to colorize
        bg_color: Background color (with or without 'bg:' prefix)
        fg_color: Foreground color
        pad_to: Optional padding length
        
    Returns:
        Colorized text string
    """
    # Handle padding
    if pad_to and len(text) < pad_to:
        text = text + ' ' * (pad_to - len(text))
    elif pad_to and len(text) > pad_to:
        text = text[:pad_to-3] + '...'
        
    # Clean up colors
    if bg_color.startswith('bg:'):
        bg_color = bg_color[3:]
        
    # For terminal output, we'll fake the colors with symbols
    # In a real terminal, we'd use ANSI escape codes
    return text