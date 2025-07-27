from os import environ
from pathlib import Path
from sys import base_prefix

environ["TCL_LIBRARY"] = str(Path(base_prefix) / "lib" / "tcl8.6")
environ["TK_LIBRARY"] = str(Path(base_prefix) / "lib" / "tk8.6")
import tkinter as tk
from typing import Optional
import threading
import time


class ActionOverlay:
    """
    A macOS-compatible overlay that displays action text on top of all applications.
    Creates Tkinter widgets on the main thread to avoid NSWindow threading issues.
    """

    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.label: Optional[tk.Label] = None
        self.is_showing = False
        self._is_initialized = False
        self._setup_overlay()

    def _setup_overlay(self):
        """Initialize the overlay window on the main thread."""
        # Defer initialization until first use to ensure main thread
        pass

    def _ensure_initialized(self):
        """Ensure the overlay is initialized (must be called from main thread)."""
        if self._is_initialized:
            return

        try:
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

            self._is_initialized = True
        except Exception as e:
            print(f"Warning: Could not initialize overlay: {e}")
            self.root = None
            self.label = None

    def show_action(self, action_text: str, duration: float = 0.5):
        """
        Display action text on the overlay.

        Args:
            action_text: The text to display
            duration: How long to show the text (in seconds)
        """
        try:
            self._ensure_initialized()
            if not self.root or not self.label:
                return

            self.label.config(text=action_text)
            self.root.deiconify()  # Show window
            self.root.lift()  # Bring to front
            self.is_showing = True

            # Hide after duration
            if duration > 0:
                self.root.after(int(duration * 1000), self.hide)
        except Exception as e:
            # Silently fail if GUI operations fail
            pass

    def hide(self):
        """Hide the overlay immediately."""
        try:
            if not self.root:
                return

            self.root.withdraw()
            self.is_showing = False
        except Exception as e:
            # Silently fail if GUI operations fail
            pass

    def update_text(self, text: str):
        """Update the displayed text without changing visibility."""
        try:
            self._ensure_initialized()
            if not self.label:
                return

            self.label.config(text=text)
        except Exception as e:
            # Silently fail if GUI operations fail
            pass

    def cleanup(self):
        """Clean up the overlay resources."""
        try:
            if self.root:
                self.root.quit()
                self.root.destroy()
                self.root = None
                self.label = None
                self._is_initialized = False
        except Exception as e:
            # Silently fail if cleanup fails
            pass


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
