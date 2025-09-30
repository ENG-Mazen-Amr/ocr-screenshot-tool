# 🖼️📝 OCR Screenshot Tool (Python App)

A lightweight, user-friendly desktop application for capturing a selected region of your screen and extracting text using OCR (Optical Character Recognition). Supports both English and Arabic languages. Built entirely in Python, this tool provides a minimal floating GUI for quick and easy text extraction.

---

## ✨ Features

- ✅ **Custom Region Selection** – Freely select and resize the screen area you want to capture.
- 🖼️ **Screenshot Capture** – Grab screenshots of the selected screen area.
- 🔤 **OCR Text Extraction** – Extracts text from screenshots in English and Arabic using Tesseract OCR.
- 📋 **Copy to Clipboard** – Easily copy the extracted text for use elsewhere.
- 🖥️ **Always-on-Top Floating GUI** – A compact, draggable window that stays on top of all other applications.
- ⚙️ **Automatic or Manual Tesseract Detection** – Automatically finds the Tesseract executable or lets you manually locate it.
- 🌐 **Direct Download Link** – Opens the official Tesseract download page if not found.

---

## 🛠️ Built With

- Python 3 (https://www.python.org/)
- Tkinter (https://docs.python.org/3/library/tkinter.html)
- Pillow (PIL) (https://python-pillow.org/)
- Pytesseract (https://github.com/madmaze/pytesseract)
- Tesseract OCR (https://tesseract-ocr.github.io/)

---

## 🚀 Getting Started

### 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/ENG-Mazen-Amr/ocr-screenshot-tool.git
cd ocr-screenshot-tool
```
Install the required packages:

```bash
pip install pillow pytesseract
```
> **Note:** You need to have Tesseract OCR installed on your system.
The app will try to find it automatically or you can manually select the executable if not found.


---
## ▶️ Running the App
```bash
python ocr_screenshot_tool.py
```
- Click "Select Area" to define the screen region to capture.

- After selection, the OCR process will extract the text (English + Arabic).

- A window will show the extracted text with an option to copy it to clipboard.

- Click Exit to close the application.

## 📝 Output
Extracted text displayed in a popup window.

Option to copy text to clipboard.


---
## 📌 Known Limitations
Tested primarily on Windows.

Requires Tesseract OCR installed separately.

Only extracts text from static screenshots.

OCR accuracy depends on screenshot quality.


---
## 📄 License
MIT License – feel free to use, modify, and distribute.


---
🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you want to change.


---
## 📧 Contact
For questions or suggestions, please open an issue or contact me on GitHub.


---
