"""
Pop Animation - Special combined animation for tooltips and UI elements
"""

import animations
import threading

class PopInAnimation:
    """Combined animation that combines fade and scale effects for a pop-in effect"""
    def __init__(self, target_object, opacity_property, scale_property, on_update=None, 
                start_scale=1.1, end_scale=1.0, duration=0.3, easing='ease_out_quad'):
        """
        Initialize a pop-in animation with fade and scale effects
        
        Args:
            target_object: The object to animate
            opacity_property: The property name for opacity (0.0-1.0)
            scale_property: The property name for scale (1.0 = normal, >1.0 = bigger)
            on_update: Callback function when animation updates
            start_scale: Initial scale factor (default 1.1 - slightly larger)
            end_scale: Final scale factor (default 1.0 - normal size)
            duration: Animation duration in seconds (default 0.3s)
            easing: Easing function to use for the animation
        """
        self.target_object = target_object
        self.opacity_property = opacity_property
        self.scale_property = scale_property
        self.on_update = on_update
        self.start_scale = start_scale
        self.end_scale = end_scale
        self.duration = duration
        self.easing = easing
        self.fade_animation = None
        self.scale_animation = None
        self.animation_lock = threading.Lock()
        
    def create_animations(self):
        """Create the component animations if they don't exist"""
        with self.animation_lock:
            # Create fade animation
            self.fade_animation = animations.FadeAnimation(
                self.target_object,
                self.opacity_property,
                0.0, 
                1.0,
                on_update=self.on_update
            )
            
            # Create scale animation
            self.scale_animation = animations.ScaleAnimation(
                self.target_object,
                self.scale_property,
                self.start_scale,  # Start slightly scaled
                self.end_scale,    # End at normal scale
                on_update=self.on_update
            )
            
            # Set animation durations
            self.fade_animation.duration = self.duration
            self.scale_animation.duration = self.duration * 0.8  # Slightly faster scale for better effect
            
    def start(self):
        """Start the pop-in animation sequence"""
        if not self.fade_animation or not self.scale_animation:
            self.create_animations()
            
        with self.animation_lock:
            # Set initial values
            if hasattr(self.target_object, self.opacity_property):
                setattr(self.target_object, self.opacity_property, 0.0)
            if hasattr(self.target_object, self.scale_property):
                setattr(self.target_object, self.scale_property, 1.1)
                
            # Start animations
            self.fade_animation.start()
            self.scale_animation.start()
            
    def stop(self):
        """Stop both animations"""
        with self.animation_lock:
            if self.fade_animation:
                self.fade_animation.stop()
            if self.scale_animation:
                self.scale_animation.stop()


class PopOutAnimation:
    """Combined animation that combines fade and scale effects for a pop-out effect"""
    def __init__(self, target_object, opacity_property, scale_property, on_update=None, on_complete=None,
                start_scale=1.0, end_scale=0.9, duration=0.25, easing='ease_in_quad'):
        """
        Initialize a pop-out animation with fade and scale effects
        
        Args:
            target_object: The object to animate
            opacity_property: The property name for opacity (0.0-1.0)
            scale_property: The property name for scale (1.0 = normal, <1.0 = smaller)
            on_update: Callback function when animation updates
            on_complete: Callback function when animation completes
            start_scale: Initial scale factor (default 1.0 - normal size)
            end_scale: Final scale factor (default 0.9 - slightly smaller)
            duration: Animation duration in seconds (default 0.25s)
            easing: Easing function to use for the animation
        """
        self.target_object = target_object
        self.opacity_property = opacity_property
        self.scale_property = scale_property
        self.on_update = on_update
        self.on_complete = on_complete
        self.start_scale = start_scale
        self.end_scale = end_scale
        self.duration = duration
        self.easing = easing
        self.fade_animation = None
        self.scale_animation = None
        self.animation_lock = threading.Lock()
        
    def create_animations(self):
        """Create the component animations if they don't exist"""
        with self.animation_lock:
            # Create fade animation
            self.fade_animation = animations.FadeAnimation(
                self.target_object,
                self.opacity_property,
                1.0, 
                0.0,
                on_update=self.on_update
            )
            
            # Create scale animation
            self.scale_animation = animations.ScaleAnimation(
                self.target_object,
                self.scale_property,
                self.start_scale,  # Start at normal scale
                self.end_scale,    # End slightly smaller
                on_update=self.on_update
            )
            
            # Set animation durations
            self.fade_animation.duration = self.duration
            self.scale_animation.duration = self.duration * 0.7  # Slightly faster scale for pop effect
            
            # Set completion callback
            original_on_complete = self.fade_animation.on_complete
            def completion_wrapper():
                original_on_complete()
                if self.on_complete:
                    self.on_complete()
            
            self.fade_animation.on_complete = completion_wrapper
            
    def start(self):
        """Start the pop-out animation sequence"""
        if not self.fade_animation or not self.scale_animation:
            self.create_animations()
            
        with self.animation_lock:
            # Set initial values
            if hasattr(self.target_object, self.opacity_property):
                setattr(self.target_object, self.opacity_property, 1.0)
            if hasattr(self.target_object, self.scale_property):
                setattr(self.target_object, self.scale_property, 1.0)
                
            # Start animations
            self.fade_animation.start()
            self.scale_animation.start()
            
    def stop(self):
        """Stop both animations"""
        with self.animation_lock:
            if self.fade_animation:
                self.fade_animation.stop()
            if self.scale_animation:
                self.scale_animation.stop()


def register_with_animation_manager(animation_manager):
    """
    Register standard pop animations with the animation manager for global access
    
    This function creates and registers commonly used pop animations for UI elements
    like tooltips, panels, and modals to be easily accessible throughout the application.
    
    Args:
        animation_manager: The AnimationManager instance to register with
    """
    # Example registrations of common animations
    def create_tooltip_pop_in(target_object):
        """Create a standard tooltip pop-in animation"""
        pop_in = PopInAnimation(
            target_object,
            "opacity",
            "scale",
            duration=0.25,
            start_scale=1.05,
            end_scale=1.0
        )
        
        # Add a wrapper to properly handle animation state
        class AnimationWrapper(animations.AnimationState):
            def __init__(self, animation):
                super().__init__()
                self.animation = animation
                self.duration = animation.duration
                
            def start(self):
                self.animating = True
                self.animation.start()
                
            def stop(self):
                self.animating = False
                self.animation.stop()
                
        return AnimationWrapper(pop_in)
    
    def create_panel_slide_in(target_object):
        """Create a standard panel slide-in animation"""
        slide_in = animations.SlideAnimation(
            target_object,
            "position",
            -100,  # Start off-screen
            0,     # End at normal position
            on_update=lambda v: target_object.refresh()
        )
        slide_in.duration = 0.35  # Slightly slower for panels
        
        return slide_in
        
    # Register standard animations
    animation_manager.add_animation("tooltip_pop_in_template", create_tooltip_pop_in)
    animation_manager.add_animation("panel_slide_in_template", create_panel_slide_in)
    
    # Additional animation registrations as needed
    animation_manager.add_animation("notification_pop_in", lambda obj: PopInAnimation(
        obj, 
        "opacity", 
        "scale", 
        duration=0.35,
        start_scale=1.1,
        end_scale=1.0,
        easing='ease_out_bounce'
    ))