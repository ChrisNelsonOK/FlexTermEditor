"""
Adaptive UI - Handles dynamic UI sizing based on screen resolution and terminal size
"""
import os
import time
import threading
from typing import Dict, Tuple, Optional, Callable, Any

class AdaptiveUI:
    """Manages UI scaling and layout adjustments based on terminal size"""
    
    # UI size categories
    SIZE_SMALL = "small"    # Minimal UI with essential components only
    SIZE_MEDIUM = "medium"  # Standard UI with most features
    SIZE_LARGE = "large"    # Full UI with all panels and features
    
    # Default minimum sizes for each category
    DEFAULT_SIZE_THRESHOLDS = {
        SIZE_SMALL: (60, 15),   # Minimum: 60 columns, 15 rows
        SIZE_MEDIUM: (80, 24),  # Standard: 80 columns, 24 rows
        SIZE_LARGE: (120, 30)   # Large: 120 columns, 30 rows
    }
    
    def __init__(self, size_thresholds: Optional[Dict[str, Tuple[int, int]]] = None):
        """Initialize the adaptive UI manager
        
        Args:
            size_thresholds: Optional custom thresholds for size categories
        """
        self.size_thresholds = size_thresholds or self.DEFAULT_SIZE_THRESHOLDS
        self.current_size_category = self.SIZE_MEDIUM  # Default
        self.current_width = 80
        self.current_height = 24
        self.terminal_monitor_active = False
        self.terminal_monitor_thread = None
        self.resize_callbacks = []
        self.last_check_time = 0
        self.resize_interval = 1.0  # Check terminal size every second
    
    def start_terminal_monitor(self) -> None:
        """Start monitoring terminal size changes in a background thread"""
        if self.terminal_monitor_active:
            return
            
        self.terminal_monitor_active = True
        self.terminal_monitor_thread = threading.Thread(
            target=self._monitor_terminal_size, 
            daemon=True
        )
        self.terminal_monitor_thread.start()
    
    def stop_terminal_monitor(self) -> None:
        """Stop the terminal size monitoring thread"""
        self.terminal_monitor_active = False
        if self.terminal_monitor_thread and self.terminal_monitor_thread.is_alive():
            self.terminal_monitor_thread.join(timeout=1.0)
    
    def _monitor_terminal_size(self) -> None:
        """Monitor terminal size in a background thread"""
        while self.terminal_monitor_active:
            try:
                # Check if enough time has passed since last check
                current_time = time.time()
                if current_time - self.last_check_time >= self.resize_interval:
                    self.last_check_time = current_time
                    
                    # Get current terminal size
                    width, height = self.get_terminal_size()
                    
                    # If size has changed, trigger resize event
                    if width != self.current_width or height != self.current_height:
                        old_category = self.current_size_category
                        self.current_width = width
                        self.current_height = height
                        self.current_size_category = self._determine_size_category(width, height)
                        
                        # Notify callbacks of resize
                        self._trigger_resize_callbacks(
                            width, height, 
                            self.current_size_category, 
                            old_category != self.current_size_category
                        )
            except Exception as e:
                # Log the error but don't crash the thread
                print(f"Error monitoring terminal size: {e}")
                
            # Sleep to avoid consuming too much CPU
            time.sleep(0.2)
    
    def get_terminal_size(self) -> Tuple[int, int]:
        """Get current terminal dimensions
        
        Returns:
            Tuple of (width, height) in characters
        """
        try:
            columns, rows = os.get_terminal_size()
            return columns, rows
        except OSError:
            # Fallback to default if can't determine terminal size
            return self.current_width, self.current_height
    
    def _determine_size_category(self, width: int, height: int) -> str:
        """Determine the appropriate size category based on terminal dimensions
        
        Args:
            width: Terminal width in characters
            height: Terminal height in characters
            
        Returns:
            Size category string (small, medium, or large)
        """
        # Start with smallest size and increase if dimensions allow
        if width < self.size_thresholds[self.SIZE_MEDIUM][0] or height < self.size_thresholds[self.SIZE_MEDIUM][1]:
            return self.SIZE_SMALL
        elif width >= self.size_thresholds[self.SIZE_LARGE][0] and height >= self.size_thresholds[self.SIZE_LARGE][1]:
            return self.SIZE_LARGE
        else:
            return self.SIZE_MEDIUM
    
    def register_resize_callback(self, callback: Callable[[int, int, str, bool], Any]) -> None:
        """Register a callback to be notified of terminal resize events
        
        Args:
            callback: Function that receives width, height, size_category, and category_changed parameters
        """
        if callback not in self.resize_callbacks:
            self.resize_callbacks.append(callback)
    
    def unregister_resize_callback(self, callback: Callable) -> None:
        """Remove a previously registered callback
        
        Args:
            callback: The callback function to remove
        """
        if callback in self.resize_callbacks:
            self.resize_callbacks.remove(callback)
    
    def _trigger_resize_callbacks(self, width: int, height: int, category: str, category_changed: bool) -> None:
        """Call all registered callbacks with the new size information
        
        Args:
            width: New terminal width in characters
            height: New terminal height in characters
            category: Size category (small, medium, large)
            category_changed: Whether the size category has changed
        """
        for callback in self.resize_callbacks:
            try:
                callback(width, height, category, category_changed)
            except Exception as e:
                print(f"Error in resize callback: {e}")
    
    def get_panel_sizes(self, 
                      available_height: int, 
                      panels: Dict[str, bool]) -> Dict[str, int]:
        """Calculate optimal panel heights based on available space and enabled panels
        
        Args:
            available_height: Total available height to distribute
            panels: Dictionary of panel names and their enabled state
            
        Returns:
            Dictionary mapping panel names to their allocated heights
        """
        # Default minimum sizes for each panel
        min_sizes = {
            "editor": 10,       # Editor panel needs minimum 10 rows
            "terminal": 6,      # Terminal needs minimum 6 rows
            "insights": 5,      # AI Insights panel needs minimum 5 rows
            "search": 3,        # Search panel needs minimum 3 rows
            "tab_bar": 1,       # Tab bar is always 1 row
            "status_bar": 1     # Status bar is always 1 row
        }
        
        # Calculate how many panels are enabled
        enabled_panels = [panel for panel, enabled in panels.items() if enabled]
        required_height = sum(min_sizes[panel] for panel in enabled_panels)
        
        # If not enough space, prioritize panels
        if required_height > available_height:
            # Priority order: editor > terminal > tab_bar > status_bar > insights > search
            priority_order = ["tab_bar", "status_bar", "editor", "terminal", "insights", "search"]
            result = {panel: 0 for panel in panels}
            
            remaining_height = available_height
            for panel in priority_order:
                if panel in enabled_panels and remaining_height > 0:
                    # Allocate minimum size or remaining height, whichever is smaller
                    allocation = min(min_sizes[panel], remaining_height)
                    result[panel] = allocation
                    remaining_height -= allocation
            
            return result
        
        # If enough space, distribute proportionally
        extra_height = available_height - required_height
        proportions = {
            "editor": 0.6,      # Editor gets 60% of extra space
            "terminal": 0.25,   # Terminal gets 25% of extra space
            "insights": 0.1,    # Insights gets 10% of extra space
            "search": 0.05,     # Search gets 5% of extra space
            "tab_bar": 0,       # Tab bar is fixed
            "status_bar": 0     # Status bar is fixed
        }
        
        result = {}
        for panel in panels:
            if panels[panel]:  # If panel is enabled
                # Start with minimum size
                panel_height = min_sizes[panel]
                
                # Add proportion of extra space
                panel_height += int(extra_height * proportions[panel])
                
                result[panel] = panel_height
            else:
                result[panel] = 0
        
        # Ensure we've allocated exactly the available height
        allocated = sum(result.values())
        if allocated < available_height:
            # Add remaining rows to editor
            result["editor"] += available_height - allocated
        
        return result
    
    def get_command_line_width(self) -> int:
        """Calculate the optimal width for command line input
        
        Returns:
            Width in characters
        """
        # Set command line width based on terminal width
        if self.current_size_category == self.SIZE_SMALL:
            return min(self.current_width - 2, 50)  # Smaller for small screens
        elif self.current_size_category == self.SIZE_LARGE:
            return min(self.current_width - 10, 120)  # Wider for large screens
        else:
            return min(self.current_width - 5, 80)  # Standard

# Singleton instance
_adaptive_ui = None

def get_adaptive_ui() -> AdaptiveUI:
    """Get the global AdaptiveUI instance
    
    Returns:
        AdaptiveUI instance
    """
    global _adaptive_ui
    if _adaptive_ui is None:
        _adaptive_ui = AdaptiveUI()
    return _adaptive_ui