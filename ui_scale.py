import platform
from guizero import Picture

IS_LINUX = platform.system() == "Linux"
SCALE = 1 if IS_LINUX else 0.6

def s(val):
    """Scale any integer dimension, padding, or font size."""
    if isinstance(val, (int, float)):
        return max(1, int(round(val * SCALE)))
    return val

def scale_picture(pic):
    """Resize a guizero Picture widget using its explicit or native image size."""
    # Check if explicit integer width/height were passed to Picture(...)
    w = pic.width if isinstance(pic.width, int) else None
    h = pic.height if isinstance(pic.height, int) else None

    # If no explicit size was set, read the native size from the underlying tk image
    if w is None or h is None:
        try:
            tk_img = pic.tk.cget("image")
            w = w or pic.tk.tk.call("image", "width", tk_img)
            h = h or pic.tk.tk.call("image", "height", tk_img)
        except Exception:
            return  # Skip if image hasn't loaded

    pic.resize(s(w), s(h))

def apply_scale(container):
    """Recursively scale an App, Window, or Box and all its child widgets."""
    if isinstance(getattr(container, "width", None), int):
        container.width = s(container.width)
    if isinstance(getattr(container, "height", None), int):
        container.height = s(container.height)

    for widget in getattr(container, "children", []):
        # Handle Picture widgets separately via .resize()
        if isinstance(widget, Picture):
            scale_picture(widget)
            continue

        # Scale text_size on all text-bearing widgets
        if getattr(widget, "text_size", None):
            widget.text_size = s(widget.text_size)

        # Scale fixed pixel width/height on non-Picture widgets
        if isinstance(getattr(widget, "width", None), int):
            widget.width = s(widget.width)
        if isinstance(getattr(widget, "height", None), int):
            widget.height = s(widget.height)

        # Recurse into nested Boxes or containers
        if hasattr(widget, "children"):
            apply_scale(widget)
