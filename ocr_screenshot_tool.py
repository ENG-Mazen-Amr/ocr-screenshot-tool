import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageGrab
import pytesseract
import os
import shutil
import sys
import json
import webbrowser

# ---------------- Configuration File ----------------
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ocr_screenshot_config.json")

def load_config():
    """Load configuration from file."""
    try:
        if os.path.isfile(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_config(cfg):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ---------------- Tesseract Path Detection ----------------
def find_or_request_tesseract(max_scan_dirs=4000, scan_drives=None):
    """
    Try to find tesseract.exe automatically.
    If not found, ask the user to locate it or download it.
    """
    cfg = load_config()

    # 1. Use previously saved path
    saved = cfg.get("tesseract_path")
    if saved and os.path.isfile(saved):
        return saved

    # 2. Check PATH
    path_candidate = shutil.which("tesseract")
    if path_candidate and os.path.isfile(path_candidate):
        cfg["tesseract_path"] = path_candidate
        save_config(cfg)
        return path_candidate

    # 3. Check common locations
    cwd = os.getcwd()
    common_paths = [
        os.path.join(cwd, "Tesseract-OCR", "tesseract.exe"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for p in common_paths:
        if os.path.isfile(p):
            cfg["tesseract_path"] = p
            save_config(cfg)
            return p

    # 4. Optional search on Windows drives
    if sys.platform.startswith("win"):
        if scan_drives is None:
            scan_drives = [f"{d}:\\" for d in "CDEF"]

        scanned_dirs = 0
        skip_names = ("$Recycle.Bin", "System Volume Information", "Windows\\WinSxS")

        for drive in scan_drives:
            if not os.path.exists(drive):
                continue
            try:
                for root, dirs, files in os.walk(drive, topdown=True):
                    scanned_dirs += 1
                    if any(skip in root for skip in skip_names):
                        dirs[:] = []
                        continue
                    for fname in files:
                        if fname.lower() == "tesseract.exe":
                            candidate = os.path.join(root, fname)
                            if os.path.isfile(candidate):
                                cfg["tesseract_path"] = candidate
                                save_config(cfg)
                                return candidate
                    if scanned_dirs >= max_scan_dirs:
                        break
            except (PermissionError, Exception):
                continue

    # 5. Prompt the user
    root = tk.Tk()
    root.withdraw()
    msg = (
        "Tesseract was not found automatically on your system.\n\n"
        "Would you like to open the official page to download Tesseract now?\n\n"
        "Click 'Yes' to open the browser, or 'No' to manually locate the tesseract.exe file."
    )

    if messagebox.askyesno("Tesseract Not Found", msg, parent=root):
        webbrowser.open("https://sourceforge.net/projects/tesseract-ocr.mirror/")
        messagebox.showinfo("After Downloading", "Once installed, please manually select the tesseract.exe file.", parent=root)

    file_path = filedialog.askopenfilename(
        title="Select Tesseract Executable (tesseract.exe)",
        filetypes=[("tesseract.exe", "tesseract.exe"), ("All files", "*.*")],
        parent=root
    )
    root.destroy()

    if file_path and os.path.isfile(file_path):
        cfg["tesseract_path"] = file_path
        save_config(cfg)
        return file_path

    return None

# ---------------- Initialize pytesseract ----------------
tesseract_path = find_or_request_tesseract()

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    print("Tesseract executable not found. OCR will not function without it.")

# ---------------- Main GUI Application ----------------
class MainApp:
    def __init__(self, master):
        self.master = master
        master.title("OCR Screenshot Tool")
        master.overrideredirect(True)
        master.attributes('-alpha', 0.85)
        master.attributes('-topmost', True)

        screen_width = master.winfo_screenwidth()
        x_pos = screen_width - 250
        y_pos = 50
        master.geometry(f"230x100+{x_pos}+{y_pos}")

        master.bind("<Button-1>", self._start_move)
        master.bind("<B1-Motion>", self._do_move)

        main_frame = tk.Frame(master, bg='black')
        main_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        main_frame.bind("<Button-1>", self._start_move)
        main_frame.bind("<B1-Motion>", self._do_move)

        self.select_button = tk.Button(main_frame, text="Select Area", command=self.start_selection)
        self.select_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

        self.exit_button = tk.Button(main_frame, text="Exit", command=self.master.quit)
        self.exit_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

    def _start_move(self, event):
        self.x = event.x
        self.y = event.y

    def _do_move(self, event):
        x_new = self.master.winfo_x() + event.x - self.x
        y_new = self.master.winfo_y() + event.y - self.y
        self.master.geometry(f"+{x_new}+{y_new}")

    def start_selection(self):
        self.master.withdraw()
        ScreenshotWindow(self.master)

# ---------------- Screenshot and OCR Window ----------------
class ScreenshotWindow:
    def __init__(self, master):
        self.master = master
        self.start_x = None
        self.start_y = None

        self.screenshot_window = tk.Toplevel(master)
        self.screenshot_window.overrideredirect(True)
        self.screenshot_window.attributes('-alpha', 0.2)
        self.screenshot_window.attributes('-topmost', True)

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        self.screenshot_window.geometry(f'{screen_width}x{screen_height}+0+0')

        self.canvas = tk.Canvas(self.screenshot_window, cursor="cross", bg="gray")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.screenshot_window.bind("<Escape>", lambda e: self.screenshot_window.destroy() or self.master.deiconify())

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)

        if x2 - x1 > 0 and y2 - y1 > 0:
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            try:
                if not getattr(pytesseract.pytesseract, "tesseract_cmd", None):
                    raise FileNotFoundError("Tesseract executable not configured.")
                text = pytesseract.image_to_string(screenshot, lang='eng+ara')
                self.display_text_window(text)
            except pytesseract.pytesseract.TesseractNotFoundError:
                self.show_error("Tesseract is not installed or the path is incorrect.")
            except Exception as e:
                self.show_error(f"An error occurred:\n{e}")

        self.screenshot_window.destroy()
        self.master.deiconify()

    def display_text_window(self, text):
        text_window = tk.Toplevel(self.master)
        text_window.title("Extracted Text")
        text_window.geometry("500x500")

        text_widget = tk.Text(text_window, wrap="word")
        text_widget.pack(expand=True, fill="both")
        text_widget.insert(tk.END, text)

        copy_button = tk.Button
        copy_button = tk.Button(text_window, text="Copy to Clipboard", command=lambda: self.copy_to_clipboard(text_widget))
        copy_button.pack(pady=5)

    def show_error(self, message):
        """Show an error message window."""
        error_window = tk.Toplevel(self.master)
        error_window.title("Error")
        tk.Label(error_window, text=message, fg="red", padx=10, pady=10).pack()
        tk.Button(error_window, text="OK", command=error_window.destroy).pack(pady=5)

    def copy_to_clipboard(self, text_widget):
        """Copy the OCR text to the clipboard."""
        try:
            text = text_widget.get("1.0", tk.END).strip()
            self.master.clipboard_clear()
            self.master.clipboard_append(text)
            self.master.update()  # now it stays on the clipboard after the window is closed
        except Exception as e:
            self.show_error(f"Failed to copy text:\n{e}")

def main():
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
