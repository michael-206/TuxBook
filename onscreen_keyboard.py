"""Simple on-screen keyboard for Tk / guizero apps."""
import tkinter as tk

# ---- look & feel -------------------------------------------------------
BG = "#ffffff"
KEY_BG = "#ffffff"
KEY_FG = "#000000"
BORDER = "#777777"
FONT = ("Arial", 36, "bold")

# Every key spans 2 of these 20 columns, which makes the half-key
# indent on the second row (and the wide shift / backspace) easy.
COLS = 20

# ---- layouts (3 rows of characters; the bottom row is fixed) -----------
LETTERS = ("qwertyuiop", "asdfghjkl", "zxcvbnm")
SYMBOLS = ("1234567890", "@#$%&-+()", "!\"':;/?")
SYMBOLS_2 = ("~`|\\^<>€£¥", "_={}[]*%", "°•§©®")

TEXT_WIDGETS = ("Entry", "TEntry", "Text", "Spinbox", "TCombobox")


class OnScreenKeyboard:
    def __init__(self, window, nav_height=120, height=420):
        self.window = window          # the Tk root (e.g. guizero_app.tk)
        self.nav_height = nav_height  # keyboard sits above the bottom bar
        self.height = height
        self.target = None            # widget currently receiving keys
        self.visible = False
        self.shift = False
        self.symbols = False

        self.frame = tk.Frame(
            window, bg=BG, highlightbackground="black", highlightthickness=2
        )
        for c in range(COLS):
            self.frame.grid_columnconfigure(c, weight=1, uniform="k")
        for r in range(4):
            self.frame.grid_rowconfigure(r, weight=1, uniform="k")
        self._build()

        # Focus doesn't always fire on touch, so listen for clicks too.
        window.bind_all("<FocusIn>", self._on_focus, add="+")
        window.bind_all("<Button-1>", self._on_focus, add="+")
        window.bind("<Configure>", self._on_resize, add="+")

    # ---- show / hide ----------------------------------------------------
    def show(self):
        self.visible = True
        self._place()
        self.window.after_idle(self._place)  # re-lift once layout settles

    def hide(self):
        self.visible = False
        self.frame.place_forget()

    def toggle(self):
        self.hide() if self.visible else self.show()

    def _place(self):
        if not self.visible:
            return
        w, h = self.window.winfo_width(), self.window.winfo_height()
        kb_h = max(1, min(self.height, h - self.nav_height))
        self.frame.place(x=0, y=h - self.nav_height - kb_h, width=w, height=kb_h)
        self.frame.lift()

    def _on_resize(self, event):
        if event.widget is self.window:
            self._place()

    def _on_focus(self, event):
        try:
            if event.widget.winfo_class() in TEXT_WIDGETS:
                self.target = event.widget
                self.show()
        except (tk.TclError, AttributeError):
            pass

    # ---- building the keys ---------------------------------------------
    def _key(self, row, col, span, label, command, inverted=False):
        bg, fg = (KEY_FG, KEY_BG) if inverted else (KEY_BG, KEY_FG)
        tk.Button(
            self.frame, text=label, command=command, font=FONT,
            bg=bg, fg=fg, activebackground="#cccccc", activeforeground=KEY_FG,
            relief="flat", bd=0, takefocus=False,
            highlightthickness=1, highlightbackground=BORDER,
        ).grid(row=row, column=col, columnspan=span, sticky="nsew", padx=3, pady=3)

    def _char_row(self, row, chars, start):
        for i, ch in enumerate(chars):
            label = ch.upper() if self.shift and not self.symbols else ch
            self._key(row, start + 2 * i, 2, label, lambda v=label: self._type(v))

    def _build(self):
        for child in self.frame.winfo_children():
            child.destroy()

        if self.symbols:
            rows = SYMBOLS_2 if self.shift else SYMBOLS
        else:
            rows = LETTERS

        # Rows 1 + 2: centred, so the 9-key row gets its half-key indent.
        for r in (0, 1):
            self._char_row(r, rows[r], (COLS - 2 * len(rows[r])) // 2)

        # Row 3: [shift] keys [backspace]
        if self.symbols:
            self._key(2, 0, 3, "2/2" if self.shift else "1/2", self._toggle_shift)
        else:
            self._key(2, 0, 3, "⇧", self._toggle_shift, inverted=self.shift)
        self._char_row(2, rows[2], 3 + (14 - 2 * len(rows[2])) // 2)
        self._key(2, 17, 3, "⌫", self._backspace)

        # Row 4: fixed
        self._key(3, 0, 3, "ABC" if self.symbols else "?123", self._toggle_symbols)
        self._key(3, 3, 2, ",", lambda: self._type(","))
        self._key(3, 5, 8, "space", lambda: self._type(" "))
        self._key(3, 13, 2, ".", lambda: self._type("."))
        self._key(3, 15, 3, "↵", self._enter)
        self._key(3, 18, 2, "↓", self.hide)

    def _rebuild_soon(self):
        # Never destroy a button from inside its own click handler.
        self.window.after_idle(self._build)

    # ---- key actions ----------------------------------------------------
    def _toggle_shift(self):
        self.shift = not self.shift
        self._rebuild_soon()

    def _toggle_symbols(self):
        self.symbols = not self.symbols
        self.shift = False
        self._rebuild_soon()

    def _widget(self):
        try:
            if self.target is not None and self.target.winfo_exists():
                return self.target
        except tk.TclError:
            pass
        self.target = None
        return None

    def _type(self, value):
        w = self._widget()
        if w is None:
            return
        try:
            try:
                w.delete("sel.first", "sel.last")  # replace selection
            except tk.TclError:
                pass
            w.insert("insert", value)
        except tk.TclError:
            return
        if self.shift and not self.symbols and value.isalpha():
            self.shift = False  # shift is one-shot
            self._rebuild_soon()

    def _backspace(self):
        w = self._widget()
        if w is None:
            return
        try:
            try:
                w.delete("sel.first", "sel.last")
            except tk.TclError:
                if w.winfo_class() == "Text":
                    w.delete("insert-1c", "insert")
                elif w.index("insert") > 0:
                    w.delete(w.index("insert") - 1)
        except tk.TclError:
            pass

    def _enter(self):
        w = self._widget()
        if w is None:
            return
        if w.winfo_class() == "Text":
            self._type("\n")
        else:
            w.event_generate("<Return>")
