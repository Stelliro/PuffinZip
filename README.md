# PuffinZip - LZMA Compression Utility

PuffinZip is a simple, user-friendly graphical application for compressing and decompressing files using the powerful LZMA algorithm, offering high compression ratios. It's designed with a clean, dark-mode interface.

![PuffinZip Screenshot](placeholder.png) 
*(Suggestion: Add a screenshot of your application here named `placeholder.png` or similar, then update the link. You can drag-and-drop images into GitHub issues/PRs/wikis to get a Markdown link.)*

## Features

*   **High Compression:** Uses LZMA (preset 9) for maximal file size reduction.
*   **User-Friendly GUI:** Simple tabbed interface built with `customtkinter`.
    *   Compress Tab: Select file, choose output name (auto-suggested), and compress.
    *   Decompress Tab: Select `.lzma` file, choose output name (auto-suggested), and decompress.
    *   Logs Tab: View detailed operation logs.
*   **Dark Mode:** Easy on the eyes.
*   **Responsive Interface:** Long operations run in background threads, keeping the UI active.
*   **Progress Indicator:** An indeterminate progress bar shows when an operation is active.
*   **Status Updates:** Clear status messages for idle, working, success, or error states.
*   **Detailed Logging:** Operations are logged to `app_puffinzip.log` (created in the same folder as the EXE) for troubleshooting or review.

## Download & Installation (for Users)

1.  Go to the [**Releases Page**](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME/releases) of this repository. 
    *(Please update this link to your actual GitHub repository's releases page!)*
2.  Download the latest `PuffinZip.exe` (or `PuffinZip_vX.Y.Z.exe`) file.
3.  Place the `.exe` file in a folder of your choice.
4.  Double-click `PuffinZip.exe` to run the application. No installation is required.

## How to Use

1.  Launch `PuffinZip.exe`. The application window will appear.

    **To Compress a File:**
    *   Navigate to the "Compress" tab.
    *   Click "Browse" to select the file you want to compress.
    *   The output filename (e.g., `yourfile.ext.lzma`) will be suggested. You can change it if needed.
    *   Click the "Compress" button.

    **To Decompress a File:**
    *   Navigate to the "Decompress" tab.
    *   Click "Browse" to select the `.lzma` file you want to decompress.
    *   The original filename will be suggested as the output. You can change it.
    *   Click the "Decompress" button.

    **Note on Performance:** PuffinZip uses LZMA's highest compression setting (preset 9). This provides excellent compression ratios but can be time-consuming, especially for larger files (even those under 100MB). The UI will remain responsive (progress bar animating) during these operations.

---

## For Developers / Running from Source

If you prefer to run PuffinZip directly from the Python source code or contribute to its development:

### Requirements

*   Python 3.6 or newer
*   `customtkinter` library

### Setup

1.  Clone the repository or download the source code.
2.  Ensure you have Python 3.6+ installed.
3.  Install the `customtkinter` library:
    ```bash
    pip install customtkinter
    ```
4.  Navigate to the source code directory and run the script:
    ```bash
    python PuffinZip.py
    ```
    *(Assuming your Python script is named `PuffinZip.py`)*

### Building an Executable from Source

You can create a standalone executable using PyInstaller:

1.  Install PyInstaller: `pip install pyinstaller`
2.  Navigate to the script's directory and run (from your terminal/command prompt):
    ```bash
    python -m PyInstaller --onefile --windowed PuffinZip.py
    ```
    *(Or `py -m PyInstaller ...` if you use the `py` launcher)*
    
    **Note for `customtkinter` Theming:** For `customtkinter` themes to work correctly in the compiled EXE, PyInstaller might need help finding the theme assets. You might need to use the `--add-data` flag. For example:
    
    First, find your `customtkinter` assets path (e.g., by running `import customtkinter, os; print(os.path.join(os.path.dirname(customtkinter.__file__), "assets"))` in Python).
    
    Then, adjust the PyInstaller command:
    ```bash
    python -m PyInstaller --onefile --windowed --add-data "FULL_PATH_TO_CUSTOMTKINTER_ASSETS;customtkinter/assets" PuffinZip.py
    ```
    Replace `FULL_PATH_TO_CUSTOMTKINTER_ASSETS` with the actual path you found. The semicolon (`;`) is for Windows; use a colon (`:`) for Linux/macOS.

---

## Credits

*   **Concept and Direction:** Stelliro
*   **Initial Core Implementation and Iterative Development:** AI Assistant (Assisted by the user)

## Contributing

Found a bug or have an idea for an improvement? Feel free to:
*   Open an issue.
*   Fork the repository, make your changes, and submit a pull request.
