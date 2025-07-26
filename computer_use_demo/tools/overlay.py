import tkinter as tk
from typing import Optional
import threading
import time


class ActionOverlay:
    """
    A macOS-compatible overlay that displays action text on top of all applications.
    Uses Tkinter with topmost flag to ensure visibility above all windows.
    """

    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.label: Optional[tk.Label] = None
        self.is_showing = False
        self._setup_overlay()

    def _setup_overlay(self):
        """Initialize the overlay window."""
        self.root = tk.Tk()

        # Configure window to be always on top and frameless
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.8)  # Semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Position at top center of screen
        overlay_width = 600
        overlay_height = 80
        x = (screen_width - overlay_width) // 2
        y = 50  # Near top of screen

        self.root.geometry(f"{overlay_width}x{overlay_height}+{x}+{y}")

        # Configure background and styling
        self.root.configure(bg="black")

        # Create label for text
        self.label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 16, "bold"),
            fg="white",
            bg="black",
            wraplength=550,
            justify="center",
        )
        self.label.pack(expand=True, fill="both", padx=10, pady=10)

        # Start hidden
        self.root.withdraw()

        # Start the Tkinter event loop in a separate thread
        self._start_event_loop()

    def _start_event_loop(self):
        """Start Tkinter event loop in a background thread."""

        def run_loop():
            if self.root:
                self.root.mainloop()

        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()

    def show_action(self, action_text: str, duration: float = 0.5):
        """
        Display action text on the overlay.

        Args:
            action_text: The text to display
            duration: How long to show the text (in seconds)
        """
        if not self.root or not self.label:
            return

        def update_display():
            if self.label and self.root:
                self.label.config(text=action_text)
                self.root.deiconify()  # Show window
                self.root.lift()  # Bring to front
                self.is_showing = True

                # Hide after duration
                if duration > 0:
                    self.root.after(int(duration * 1000), self.hide)

        # Schedule the update on the main thread
        if self.root:
            self.root.after(0, update_display)

    def hide(self):
        """Hide the overlay immediately."""
        if not self.root:
            return

        def hide_display():
            if self.root:
                self.root.withdraw()
                self.is_showing = False

        self.root.after(0, hide_display)

    def update_text(self, text: str):
        """Update the displayed text without changing visibility."""
        if not self.label or not self.root:
            return

        def update_label():
            if self.label:
                self.label.config(text=text)

        self.root.after(0, update_label)

    def cleanup(self):
        """Clean up the overlay resources."""
        if self.root:
            self.root.quit()
            self.root.destroy()
            self.root = None
            self.label = None


# Global overlay instance
_overlay_instance: Optional[ActionOverlay] = None


def get_overlay() -> ActionOverlay:
    """Get or create the global overlay instance."""
    global _overlay_instance
    if _overlay_instance is None:
        _overlay_instance = ActionOverlay()
    return _overlay_instance


def cleanup_overlay():
    """Clean up the global overlay instance."""
    global _overlay_instance
    if _overlay_instance:
        _overlay_instance.cleanup()
        _overlay_instance = None
