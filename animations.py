"""
Animations - Provides animation framework for UI elements
"""

import threading
import time
import math

class AnimationState:
    """Base class for animation state tracking"""
    def __init__(self):
        self.animating = False
        self.start_time = 0
        self.current_step = 0
        self.max_steps = 10  # Default number of animation frames
        self.duration = 0.3  # Default animation duration in seconds
        self.timer = None
        
    def start(self):
        """Start the animation"""
        self.animating = True
        self.current_step = 0
        self.start_time = time.time()
        self.schedule_next_frame()
        
    def stop(self):
        """Stop the animation immediately"""
        self.animating = False
        if self.timer:
            self.timer.cancel()
            self.timer = None
            
    def schedule_next_frame(self):
        """Schedule the next animation frame"""
        if not self.animating:
            return
            
        step_duration = self.duration / self.max_steps
        self.timer = threading.Timer(step_duration, self._advance)
        self.timer.daemon = True  # Don't prevent application exit
        self.timer.start()
        
    def _advance(self):
        """Advance the animation to the next frame"""
        if not self.animating:
            return
            
        self.current_step += 1
        
        # Check if animation is complete
        if self.current_step >= self.max_steps:
            self.on_complete()
            return
            
        # Schedule next frame
        self.on_frame()
        self.schedule_next_frame()
        
    def on_frame(self):
        """Called on each animation frame - override in subclasses"""
        pass
        
    def on_complete(self):
        """Called when animation completes - override in subclasses"""
        self.animating = False
        
    def get_progress(self):
        """Get the current animation progress from 0.0 to 1.0"""
        if self.current_step >= self.max_steps:
            return 1.0
        return self.current_step / self.max_steps
        
    def get_eased_progress(self, easing_function="ease_out_quad"):
        """Get the current animation progress with easing applied"""
        linear_progress = self.get_progress()
        
        # Apply easing function
        if easing_function == "linear":
            return linear_progress
        elif easing_function == "ease_in_quad":
            return linear_progress * linear_progress
        elif easing_function == "ease_out_quad":
            return -(linear_progress * (linear_progress - 2))
        elif easing_function == "ease_in_out_quad":
            p = linear_progress * 2
            if p < 1:
                return 0.5 * p * p
            p -= 1
            return -0.5 * (p * (p - 2) - 1)
        elif easing_function == "ease_out_bounce":
            if linear_progress < (1/2.75):
                return 7.5625 * linear_progress * linear_progress
            elif linear_progress < (2/2.75):
                p = linear_progress - (1.5/2.75)
                return 7.5625 * p * p + 0.75
            elif linear_progress < (2.5/2.75):
                p = linear_progress - (2.25/2.75)
                return 7.5625 * p * p + 0.9375
            else:
                p = linear_progress - (2.625/2.75)
                return 7.5625 * p * p + 0.984375
        elif easing_function == "ease_in_elastic":
            if linear_progress == 0 or linear_progress == 1:
                return linear_progress
            p = linear_progress - 1
            return -(math.pow(2, 10 * p) * math.sin((p * 40 - 3) * math.pi / 6))
        elif easing_function == "ease_out_elastic":
            if linear_progress == 0 or linear_progress == 1:
                return linear_progress
            return math.pow(2, -10 * linear_progress) * math.sin((linear_progress * 40 - 3) * math.pi / 6) + 1
            
        # Default to linear
        return linear_progress


class FadeAnimation(AnimationState):
    """Animation for fading elements in/out"""
    def __init__(self, target_object, property_name, start_value=0.0, end_value=1.0, on_update=None):
        super().__init__()
        self.target_object = target_object
        self.property_name = property_name
        self.start_value = float(start_value)  # Convert to float to ensure compatibility
        self.end_value = float(end_value)      # Convert to float to ensure compatibility
        self.on_update = on_update
        
    def on_frame(self):
        """Update the target property on each frame"""
        progress = self.get_eased_progress("ease_out_quad")
        current_value = self.start_value + (self.end_value - self.start_value) * progress
        
        # Update the target property
        if hasattr(self.target_object, self.property_name):
            setattr(self.target_object, self.property_name, current_value)
            
        # Call the update callback if provided
        if self.on_update:
            self.on_update(current_value)


class SlideAnimation(AnimationState):
    """Animation for sliding elements from one position to another"""
    def __init__(self, target_object, property_name, start_pos, end_pos, on_update=None):
        super().__init__()
        self.target_object = target_object
        self.property_name = property_name
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.on_update = on_update
        
    def on_frame(self):
        """Update the target property on each frame"""
        progress = self.get_eased_progress("ease_out_quad")
        current_pos = self.start_pos + (self.end_pos - self.start_pos) * progress
        
        # Update the target property
        if hasattr(self.target_object, self.property_name):
            setattr(self.target_object, self.property_name, current_pos)
            
        # Call the update callback if provided
        if self.on_update:
            self.on_update(current_pos)


class ScaleAnimation(AnimationState):
    """Animation for scaling elements"""
    def __init__(self, target_object, property_name, start_scale=1.0, end_scale=1.5, on_update=None):
        super().__init__()
        self.target_object = target_object
        self.property_name = property_name
        self.start_scale = start_scale
        self.end_scale = end_scale
        self.on_update = on_update
        
    def on_frame(self):
        """Update the target property on each frame"""
        progress = self.get_eased_progress("ease_out_elastic")
        current_scale = self.start_scale + (self.end_scale - self.start_scale) * progress
        
        # Update the target property
        if hasattr(self.target_object, self.property_name):
            setattr(self.target_object, self.property_name, current_scale)
            
        # Call the update callback if provided
        if self.on_update:
            self.on_update(current_scale)


class BlinkAnimation(AnimationState):
    """Animation for blinking elements on/off"""
    def __init__(self, target_object, property_name, blink_count=3, on_update=None):
        super().__init__()
        self.target_object = target_object
        self.property_name = property_name
        self.blink_count = blink_count
        self.on_update = on_update
        self.max_steps = blink_count * 2  # Two steps per blink (on/off)
        
    def on_frame(self):
        """Update the target property on each frame"""
        # Alternate between 0 and 1 for each step
        value = 1 if (self.current_step % 2) == 0 else 0
        
        # Update the target property
        if hasattr(self.target_object, self.property_name):
            setattr(self.target_object, self.property_name, value)
            
        # Call the update callback if provided
        if self.on_update:
            self.on_update(value)


class AnimationManager:
    """Manages multiple animations"""
    def __init__(self):
        self.animations = {}
        
    def add_animation(self, name, animation):
        """Add an animation to the manager"""
        self.animations[name] = animation
        return animation
        
    def start_animation(self, name):
        """Start an animation by name"""
        if name in self.animations:
            self.animations[name].start()
            return True
        return False
        
    def stop_animation(self, name):
        """Stop an animation by name"""
        if name in self.animations:
            self.animations[name].stop()
            return True
        return False
        
    def stop_all_animations(self):
        """Stop all animations"""
        for animation in self.animations.values():
            animation.stop()
            
    def remove_animation(self, name):
        """Remove an animation from the manager"""
        if name in self.animations:
            self.animations[name].stop()
            del self.animations[name]
            return True
        return False
        
# Create a global animation manager instance
animation_manager = AnimationManager()