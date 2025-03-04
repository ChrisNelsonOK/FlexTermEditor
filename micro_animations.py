"""
Micro-Animations - Subtle visual feedback animations for UI elements
"""

import threading
import time
import math
import animations
import pop_animation

class MicroAnimations:
    """
    Handles small, subtle animations for UI elements to provide visual feedback
    for interactions like button presses, toggles, and focus changes.
    """
    def __init__(self, animation_manager=None):
        """Initialize with the animation manager"""
        self.animation_manager = animation_manager or animations.animation_manager
        self.register_animations()
        
    def register_animations(self):
        """Register all micro-animations with the animation manager"""
        # Button press animation
        self.animation_manager.add_animation(
            "button_press", 
            lambda obj: pop_animation.PopInAnimation(
                obj,
                "scale",
                "scale",
                start_scale=0.95,  # Slightly smaller
                end_scale=1.0,     # Back to normal
                duration=0.15,     # Very quick
                easing='ease_out_quad'
            )
        )
        
        # Toggle on animation
        self.animation_manager.add_animation(
            "toggle_on", 
            lambda obj: animations.FadeAnimation(
                obj,
                "highlight",
                0.0,
                1.0,
                on_update=lambda v: self._refresh_ui()
            )
        )
        
        # Toggle off animation
        self.animation_manager.add_animation(
            "toggle_off", 
            lambda obj: animations.FadeAnimation(
                obj,
                "highlight",
                1.0,
                0.0,
                on_update=lambda v: self._refresh_ui()
            )
        )
        
        # Focus change animation for panels
        self.animation_manager.add_animation(
            "panel_focus", 
            lambda obj: animations.FadeAnimation(
                obj,
                "border_highlight",
                0.0,
                1.0,
                on_update=lambda v: self._refresh_ui()
            )
        )
        
        # Notification pulse animation
        self.animation_manager.add_animation(
            "notification_pulse",
            self._create_pulse_animation
        )
        
        # Tab activation flash
        self.animation_manager.add_animation(
            "tab_flash",
            lambda obj: animations.FadeAnimation(
                obj,
                "flash_highlight",
                0.0,
                1.0,
                on_update=lambda v: self._refresh_ui()
            )
        )
        
    def _create_pulse_animation(self, obj):
        """Create a pulsing animation for notifications"""
        class PulseAnimation(animations.AnimationState):
            def __init__(self, target_obj):
                super().__init__()
                self.target_obj = target_obj
                self.duration = 1.5  # Longer duration for full pulse cycle
                self.pulse_count = 3  # Number of pulses
                self.current_pulse = 0
                
            def on_frame(self):
                """Update the pulse effect on each frame"""
                # Calculate pulse effect (0.0 to 1.0 to 0.0)
                pulse_progress = self.get_progress() * self.pulse_count
                pulse_phase = pulse_progress - int(pulse_progress)
                pulse_value = 1.0 - abs(pulse_phase * 2.0 - 1.0)  # Triangle wave
                
                # Apply to target object
                if hasattr(self.target_obj, "pulse_intensity"):
                    setattr(self.target_obj, "pulse_intensity", pulse_value)
                
                # Request UI refresh
                micro_animations._refresh_ui()
                
        return PulseAnimation(obj)
    
    def _refresh_ui(self):
        """Refresh the UI to show animation changes"""
        try:
            # This will be properly set when the editor app is initialized
            from editor_core import refresh_editor_view
            refresh_editor_view()
        except (ImportError, AttributeError):
            pass
    
    def animate_button_press(self, button_obj):
        """Animate a button press effect"""
        animation_name = f"button_press_{id(button_obj)}"
        
        # Create instance-specific animation if needed
        if animation_name not in self.animation_manager.animations:
            button_animation = self.animation_manager.animations["button_press"](button_obj)
            self.animation_manager.add_animation(animation_name, button_animation)
            
        # Start the animation
        self.animation_manager.start_animation(animation_name)
        
    def animate_toggle(self, toggle_obj, state):
        """Animate a toggle switch effect"""
        animation_name = f"toggle_{id(toggle_obj)}"
        
        # Create instance-specific animation if needed
        base_animation = "toggle_on" if state else "toggle_off"
        if animation_name not in self.animation_manager.animations:
            toggle_animation = self.animation_manager.animations[base_animation](toggle_obj)
            self.animation_manager.add_animation(animation_name, toggle_animation)
        
        # Start the animation
        self.animation_manager.start_animation(animation_name)
    
    def animate_panel_focus(self, panel_obj):
        """Animate a panel gaining focus"""
        animation_name = f"panel_focus_{id(panel_obj)}"
        
        # Create instance-specific animation if needed
        if animation_name not in self.animation_manager.animations:
            focus_animation = self.animation_manager.animations["panel_focus"](panel_obj)
            self.animation_manager.add_animation(animation_name, focus_animation)
            
        # Start the animation
        self.animation_manager.start_animation(animation_name)
    
    def animate_notification(self, notification_obj):
        """Animate a notification with pulse effect"""
        animation_name = f"notification_{id(notification_obj)}"
        
        # Create instance-specific animation if needed
        if animation_name not in self.animation_manager.animations:
            pulse_animation = self.animation_manager.animations["notification_pulse"](notification_obj)
            self.animation_manager.add_animation(animation_name, pulse_animation)
            
        # Start the animation
        self.animation_manager.start_animation(animation_name)
    
    def animate_tab_activation(self, tab_obj):
        """Animate a tab being activated"""
        animation_name = f"tab_flash_{id(tab_obj)}"
        
        # Create instance-specific animation if needed
        if animation_name not in self.animation_manager.animations:
            flash_animation = self.animation_manager.animations["tab_flash"](tab_obj)
            flash_animation.duration = 0.2  # Very quick flash
            self.animation_manager.add_animation(animation_name, flash_animation)
            
        # Start the animation
        self.animation_manager.start_animation(animation_name)
    
    def animate_cursor_blink(self, cursor_obj, blink_rate=0.53):
        """Animate cursor blinking at the specified rate"""
        animation_name = f"cursor_blink_{id(cursor_obj)}"
        
        # Create a simple blink animation
        class BlinkAnimation(animations.AnimationState):
            def __init__(self, target):
                super().__init__()
                self.target = target
                self.duration = blink_rate
                self.repeat = True  # Repeat indefinitely
                
            def on_frame(self):
                # Calculate blink state (0 or 1)
                blink_progress = self.get_progress()
                blink_value = 1.0 if blink_progress < 0.5 else 0.0
                
                # Apply to target object
                if hasattr(self.target, "visibility"):
                    setattr(self.target, "visibility", blink_value)
                
                # Request UI refresh
                micro_animations._refresh_ui()
        
        # Create the animation if needed
        if animation_name not in self.animation_manager.animations:
            blink_animation = BlinkAnimation(cursor_obj)
            self.animation_manager.add_animation(animation_name, blink_animation)
            
        # Start the animation
        self.animation_manager.start_animation(animation_name)
    
    def animate_search_result(self, result_obj, is_current=False):
        """Animate a search result highlight
        
        Args:
            result_obj: The object representing the search result
            is_current: Whether this is the currently selected result
        """
        animation_name = f"search_result_{id(result_obj)}"
        
        # Create different animations for current vs other results
        if is_current:
            # Current result gets a pulsing highlight animation
            class CurrentResultAnimation(animations.AnimationState):
                def __init__(self, target):
                    super().__init__()
                    self.target = target
                    self.duration = 1.2  # Slightly longer for a noticeable effect
                    self.repeat = True  # Keep pulsing
                    
                def on_frame(self):
                    # Calculate pulse effect (0.7 to 1.0 to 0.7)
                    pulse_progress = self.get_progress()
                    # Use sine wave for smooth pulsing
                    pulse_value = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(pulse_progress * 2 * math.pi))
                    
                    # Apply to target object
                    if hasattr(self.target, "highlight_intensity"):
                        setattr(self.target, "highlight_intensity", pulse_value)
                    
                    # Request UI refresh
                    micro_animations._refresh_ui()
            
            # Create or update the animation
            if animation_name in self.animation_manager.animations:
                self.animation_manager.remove_animation(animation_name)
            
            current_anim = CurrentResultAnimation(result_obj)
            self.animation_manager.add_animation(animation_name, current_anim)
            self.animation_manager.start_animation(animation_name)
        else:
            # Regular results get a brief fade-in animation
            class ResultFadeInAnimation(animations.AnimationState):
                def __init__(self, target):
                    super().__init__()
                    self.target = target
                    self.duration = 0.3  # Quick fade in
                    
                def on_frame(self):
                    progress = self.get_eased_progress("ease_out_quad")
                    
                    # Apply to target object - fade in from 0.2 to 0.7
                    if hasattr(self.target, "highlight_intensity"):
                        setattr(self.target, "highlight_intensity", 0.2 + (0.5 * progress))
                    
                    # Request UI refresh
                    micro_animations._refresh_ui()
            
            # Create a new animation if doesn't exist
            if animation_name not in self.animation_manager.animations:
                fade_in = ResultFadeInAnimation(result_obj)
                self.animation_manager.add_animation(animation_name, fade_in)
                self.animation_manager.start_animation(animation_name)
    
    def animate_search_navigation(self, result_obj):
        """Animate navigation to a search result
        
        This creates a brief "pop" effect when navigating to a result
        """
        animation_name = f"search_nav_{id(result_obj)}"
        
        class NavigationAnimation(animations.AnimationState):
            def __init__(self, target):
                super().__init__()
                self.target = target
                self.duration = 0.4  # Moderate duration
                
            def on_frame(self):
                progress = self.get_eased_progress("elastic_out")
                
                # Scale from 1.0 to 1.2 and back to 1.0
                if progress < 0.5:
                    # First half: scale up
                    scale = 1.0 + (0.2 * (progress * 2))
                else:
                    # Second half: scale back down
                    scale = 1.2 - (0.2 * ((progress - 0.5) * 2))
                
                # Apply to target object
                if hasattr(self.target, "scale"):
                    setattr(self.target, "scale", scale)
                
                # Also set highlight to maximum
                if hasattr(self.target, "highlight_intensity"):
                    setattr(self.target, "highlight_intensity", 1.0)
                
                # Request UI refresh
                micro_animations._refresh_ui()
            
            def on_complete(self):
                # Return to normal highlight intensity
                if hasattr(self.target, "highlight_intensity"):
                    setattr(self.target, "highlight_intensity", 0.7)
                # Return to normal scale
                if hasattr(self.target, "scale"):
                    setattr(self.target, "scale", 1.0)
                # Request UI refresh
                micro_animations._refresh_ui()
        
        # Create or update the animation
        if animation_name in self.animation_manager.animations:
            self.animation_manager.remove_animation(animation_name)
        
        nav_anim = NavigationAnimation(result_obj)
        self.animation_manager.add_animation(animation_name, nav_anim)
        self.animation_manager.start_animation(animation_name)
    
    def animate_code_completion_popup(self, popup_obj, appearing=True):
        """Animate code completion popup appearing/disappearing
        
        Args:
            popup_obj: The object representing the popup
            appearing: True if appearing, False if disappearing
        """
        animation_name = f"completion_popup_{id(popup_obj)}"
        
        # Import pop_animation for combined effects
        import pop_animation
        
        # Set animation state flags
        if hasattr(popup_obj, "animating"):
            popup_obj.animating = True
            popup_obj.animation_direction = "in" if appearing else "out"
        
        # Remove any existing animation
        if animation_name in self.animation_manager.animations:
            self.animation_manager.remove_animation(animation_name)
        
        if appearing:
            # Create a wrapper for the PopInAnimation
            class PopupAppearWrapper(animations.AnimationState):
                def __init__(self, target):
                    super().__init__()
                    self.target = target
                    self.duration = 0.25  # Slightly longer for a smoother effect
                    
                    # Create the pop-in animation
                    self.pop_animation = pop_animation.PopInAnimation(
                        target,
                        "opacity",  # Opacity property
                        "scale",    # Scale property
                        on_update=lambda _: micro_animations._refresh_ui(),
                        start_scale=1.05,  # Start slightly larger
                        end_scale=1.0,     # End at normal size
                        duration=self.duration,
                        easing='ease_out_cubic'  # Smooth ease out
                    )
                
                def start(self):
                    """Start the pop animation"""
                    self.animating = True
                    self.pop_animation.start()
                
                def stop(self):
                    """Stop the pop animation"""
                    self.animating = False
                    self.pop_animation.stop()
                    
                def on_complete(self):
                    """Animation completion callback"""
                    # Ensure the completion popup is fully visible
                    if hasattr(self.target, "opacity"):
                        self.target.opacity = 1.0
                    if hasattr(self.target, "scale"):
                        self.target.scale = 1.0
                    if hasattr(self.target, "animating"):
                        self.target.animating = False
                    micro_animations._refresh_ui()
            
            # Create the animation
            popup_anim = PopupAppearWrapper(popup_obj)
        else:
            # Create a wrapper for the PopOutAnimation
            class PopupDisappearWrapper(animations.AnimationState):
                def __init__(self, target):
                    super().__init__()
                    self.target = target
                    self.duration = 0.2  # Quick disappearance
                    
                    # Create the pop-out animation
                    self.pop_animation = pop_animation.PopOutAnimation(
                        target,
                        "opacity",  # Opacity property
                        "scale",    # Scale property
                        on_update=lambda _: micro_animations._refresh_ui(),
                        on_complete=lambda: self._on_complete_callback(),
                        start_scale=1.0,   # Start at normal size
                        end_scale=0.95,    # End slightly smaller
                        duration=self.duration,
                        easing='ease_in_quad'  # Quick ease in
                    )
                
                def _on_complete_callback(self):
                    """Internal callback when animation completes"""
                    if hasattr(self.target, "animating"):
                        self.target.animating = False
                    micro_animations._refresh_ui()
                
                def start(self):
                    """Start the pop animation"""
                    self.animating = True
                    self.pop_animation.start()
                
                def stop(self):
                    """Stop the pop animation"""
                    self.animating = False
                    self.pop_animation.stop()
                    
                def on_complete(self):
                    """Animation completion callback"""
                    # Ensure the completion popup is fully hidden
                    if hasattr(self.target, "opacity"):
                        self.target.opacity = 0.0
                    if hasattr(self.target, "animating"):
                        self.target.animating = False
                    micro_animations._refresh_ui()
            
            # Create the animation
            popup_anim = PopupDisappearWrapper(popup_obj)
            
        # Add and start the animation
        self.animation_manager.add_animation(animation_name, popup_anim)
        self.animation_manager.start_animation(animation_name)
    
    def animate_completion_selection(self, item_obj):
        """Animate selection of a completion item
        
        This creates a brief highlight effect when selecting an item
        """
        animation_name = f"completion_select_{id(item_obj)}"
        
        class SelectionAnimation(animations.AnimationState):
            def __init__(self, target):
                super().__init__()
                self.target = target
                self.duration = 0.25
                
            def on_frame(self):
                progress = self.get_eased_progress("ease_out_quad")
                
                # Create a flash effect (brighten then fade slightly)
                if progress < 0.5:
                    # First half: increase highlight from 0.5 to 1.0
                    highlight = 0.5 + (0.5 * (progress * 2))
                else:
                    # Second half: decrease highlight from 1.0 to 0.8
                    highlight = 1.0 - (0.2 * ((progress - 0.5) * 2))
                
                # Apply to target object
                if hasattr(self.target, "highlight_intensity"):
                    setattr(self.target, "highlight_intensity", highlight)
                
                # Request UI refresh
                micro_animations._refresh_ui()
            
            def on_complete(self):
                # Return to normal highlight
                if hasattr(self.target, "highlight_intensity"):
                    setattr(self.target, "highlight_intensity", 0.8)
                # Request UI refresh
                micro_animations._refresh_ui()
        
        # Create or update the animation
        if animation_name in self.animation_manager.animations:
            self.animation_manager.remove_animation(animation_name)
        
        select_anim = SelectionAnimation(item_obj)
        self.animation_manager.add_animation(animation_name, select_anim)
        self.animation_manager.start_animation(animation_name)
    
    def stop_animation(self, obj):
        """Stop any animations for the given object"""
        # Try to find and stop animations for this object
        animation_prefixes = [
            f"button_press_{id(obj)}", 
            f"toggle_{id(obj)}", 
            f"panel_focus_{id(obj)}",
            f"notification_{id(obj)}",
            f"tab_flash_{id(obj)}",
            f"cursor_blink_{id(obj)}",
            f"search_result_{id(obj)}",
            f"search_nav_{id(obj)}",
            f"completion_popup_{id(obj)}",
            f"completion_select_{id(obj)}"
        ]
        
        for prefix in animation_prefixes:
            if prefix in self.animation_manager.animations:
                self.animation_manager.stop_animation(prefix)

# Create a singleton instance
micro_animations = MicroAnimations()

def get_micro_animations():
    """Get the global micro animations instance"""
    return micro_animations