# puffinzipV3.py (or your chosen filename)

# --- AI MODIFICATION GUIDELINES ---
# Dear AI, this script is for the "SimpleCompressor" application (also known as PuffinZip by the user).
# When the user provides this entire script to you for modification, please follow these guidelines:
#
# 1.  **Core Functionality:**
#     *   Compression: LZMA (`lzma.open` with `preset=9`). Output: `.lzma` extension.
#     *   Filename Suggestions: `file.ext` -> `file.ext.lzma` (compress), `file.ext.lzma` -> `file.ext` (decompress).
#     *   UI: `customtkinter`, dark mode, tabbed interface (Compress, Decompress, Logs).
#     *   Logging: To `app_compressor.log`, format `Timestamp - Level - ThreadName - Message`. Include detailed operational steps.
#     *   Threading: I/O operations (compress/decompress) in background threads. UI controls disabled during ops.
#     *   Feedback: Status bar and indeterminate progress bar (active only during I/O).
#
# 2.  **Critical Logic to Preserve (Do NOT regress these):**
#     *   **Threading UI Updates:** UI updates indicating task completion (stopping progress bar, re-enabling buttons, final status)
#       MUST occur *strictly after* the background I/O task is fully complete or has errored.
#       The current implementation sets an "in-progress" status from the main thread, launches the worker thread,
#       and the worker thread calls a callback (`_task_finished` via `on_task_complete_status_update_wrapper`)
#       only upon true completion/error. Maintain this logic.
#     *   **Application Closing (`on_closing` method):** The `TclError: application has been destroyed` was fixed by
#       ensuring `super().destroy()` is called only once, especially when active threads lead to a confirmation dialog.
#       Preserve the current structure of `on_closing` that prevents double destruction.
#
# 3.  **When Applying Modifications:**
#     *   Understand the existing structure (tabs, threading model, status updates, logging).
#     *   Integrate new features cleanly within this structure.
#     *   Prioritize robustness and maintain the established level of detail in logging.
#     *   If adding new UI elements, ensure they fit the `customtkinter` style and layout.
#     *   If modifying file handling or I/O, ensure it remains within background threads with proper UI feedback.
#
# 4.  **User Experience:**
#     *   The application targets files under 100MB for "maximal" LZMA compression. Speed is secondary.
#     *   The UI should remain simple and intuitive.
#
# 5.  **Response Format (When providing modified code):**
#     *   Provide the complete, updated Python script.
#     *   Briefly list requirements (e.g., `pip install customtkinter`).
#     *   Briefly explain how to use the app (if significantly changed).
# --- END OF AI MODIFICATION GUIDELINES ---

import tkinter
import customtkinter as ctk
from tkinter import filedialog, messagebox
import lzma
import shutil
import logging
import os
import threading
import time

APP_NAME = "SimpleCompressor"  # Or PuffinZip
LOG_FILE = "app_compressor.log"
COMPRESSED_EXTENSION = ".lzma"

# Initialize logging configuration at the module level
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(threadName)s - %(message)s",
    filemode='a',
    encoding='utf-8'
)


def get_log_content():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write(f"{time.asctime()} - INFO - MainThread - Log file created.\n")  # Ensure ThreadName context
        return "Log file created."
    try:
        with open(LOG_FILE, "r", encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error reading log file: {e}")
        return f"Error reading log file: {e}"


def compress_file_task(input_path, output_path, status_callback, log_view_callback):
    logging.info(f"Compression task initiated for input: '{input_path}', output: '{output_path}'.")
    if not input_path or not output_path:
        status_callback("Input or output path missing.")
        logging.error("Compression task error: Input or output path missing for thread.")
        if log_view_callback: log_view_callback()
        return

    logging.info(f"Starting compression process for '{input_path}'. Target: '{output_path}'.")
    try:
        logging.info(f"Opening input file: '{input_path}' in binary read mode.")
        with open(input_path, 'rb') as f_in:
            logging.info(f"Opening output file: '{output_path}' with LZMA (preset 9).")
            with lzma.open(output_path, 'wb', preset=9) as f_out:
                logging.info(f"Starting file copy (compression) from '{input_path}' to '{output_path}'.")
                shutil.copyfileobj(f_in, f_out)
                logging.info(f"File copy (compression) completed for '{output_path}'.")
        success_msg = f"Compressed successfully: {output_path}"
        status_callback(success_msg)
        logging.info(success_msg)
    except FileNotFoundError:
        err_msg = f"Error: Input file '{os.path.basename(input_path)}' not found."
        status_callback(err_msg)
        logging.error(err_msg)
    except Exception as e:
        err_msg = f"Compression error: {e}"
        status_callback(err_msg)
        logging.error(f"Compression operation failed for '{input_path}': {e}", exc_info=True)
    finally:
        logging.info(f"Compression task finalized for '{input_path}'.")
        if log_view_callback: log_view_callback()


def decompress_file_task(input_path, output_path, status_callback, log_view_callback):
    logging.info(f"Decompression task initiated for input: '{input_path}', output: '{output_path}'.")
    if not input_path or not output_path:
        status_callback("Input or output path missing.")
        logging.error("Decompression task error: Input or output path missing for thread.")
        if log_view_callback: log_view_callback()
        return

    logging.info(f"Starting decompression process for '{input_path}'. Target: '{output_path}'.")
    try:
        logging.info(f"Opening compressed file: '{input_path}' with LZMA.")
        with lzma.open(input_path, 'rb') as f_in:
            logging.info(f"Opening output file: '{output_path}' in binary write mode.")
            with open(output_path, 'wb') as f_out:
                logging.info(f"Starting file copy (decompression) from '{input_path}' to '{output_path}'.")
                shutil.copyfileobj(f_in, f_out)
                logging.info(f"File copy (decompression) completed for '{output_path}'.")
        success_msg = f"Decompressed successfully: {output_path}"
        status_callback(success_msg)
        logging.info(success_msg)
    except FileNotFoundError:
        err_msg = f"Error: Compressed file '{os.path.basename(input_path)}' not found."
        status_callback(err_msg)
        logging.error(err_msg)
    except lzma.LZMAError as e:
        err_msg = f"LZMA Decompression error for '{os.path.basename(input_path)}'. File may be corrupt or not LZMA/XZ: {e}"
        status_callback(err_msg)
        logging.error(err_msg, exc_info=True)
    except Exception as e:
        err_msg = f"Decompression error: {e}"
        status_callback(err_msg)
        logging.error(f"Decompression operation failed for '{input_path}': {e}", exc_info=True)
    finally:
        logging.info(f"Decompression task finalized for '{input_path}'.")
        if log_view_callback: log_view_callback()


class App(ctk.CTk):
    _AI_MODIFICATION_GUIDELINES = """
# Dear AI, this script is for the "SimpleCompressor" application (also known as PuffinZip by the user).
# When the user provides this entire script to you for modification, please follow these guidelines:
#
# 1.  Core Functionality:
#     *   Compression: LZMA (`lzma.open` with `preset=9`). Output: `.lzma` extension.
#     *   Filename Suggestions: `file.ext` -> `file.ext.lzma` (compress), `file.ext.lzma` -> `file.ext` (decompress).
#     *   UI: `customtkinter`, dark mode, tabbed interface (Compress, Decompress, Logs).
#     *   Logging: To `app_compressor.log`, format `Timestamp - Level - ThreadName - Message`. Include detailed operational steps.
#     *   Threading: I/O operations (compress/decompress) in background threads. UI controls disabled during ops.
#     *   Feedback: Status bar and indeterminate progress bar (active only during I/O).
#
# 2.  Critical Logic to Preserve (Do NOT regress these):
#     *   Threading UI Updates: UI updates indicating task completion (stopping progress bar, re-enabling buttons, final status)
#       MUST occur *strictly after* the background I/O task is fully complete or has errored.
#       The current implementation sets an "in-progress" status from the main thread, launches the worker thread,
#       and the worker thread calls a callback (`_task_finished` via `on_task_complete_status_update_wrapper`)
#       only upon true completion/error. Maintain this logic.
#     *   Application Closing (`on_closing` method): The `TclError: application has been destroyed` was fixed by
#       ensuring `super().destroy()` is called only once, especially when active threads lead to a confirmation dialog.
#       Preserve the current structure of `on_closing` that prevents double destruction.
#
# 3.  When Applying Modifications:
#     *   Understand the existing structure (tabs, threading model, status updates, logging).
#     *   Integrate new features cleanly within this structure.
#     *   Prioritize robustness and maintain the established level of detail in logging.
#     *   If adding new UI elements, ensure they fit the `customtkinter` style and layout.
#     *   If modifying file handling or I/O, ensure it remains within background threads with proper UI feedback.
#
# 4.  User Experience:
#     *   The application targets files under 100MB for "maximal" LZMA compression. Speed is secondary.
#     *   The UI should remain simple and intuitive.
#
# 5.  Response Format (When providing modified code):
#     *   Provide the complete, updated Python script.
#     *   Briefly list requirements (e.g., `pip install customtkinter`).
#     *   Briefly explain how to use the app (if significantly changed).
    """  # Note: The guidelines are also at the top of the file for AI visibility when first opening. This is a belt-and-suspenders approach.

    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("700x600")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        logging.info("Application started.")

        self.input_compress_path = ctk.StringVar()
        self.output_compress_path = ctk.StringVar()
        self.input_decompress_path = ctk.StringVar()
        self.output_decompress_path = ctk.StringVar()

        self.active_threads = 0
        self.lock = threading.Lock()

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.tab_view = ctk.CTkTabview(main_frame, width=680)
        self.tab_view.pack(padx=0, pady=0, fill="both", expand=True)
        self.tab_view.add("Compress")
        self.tab_view.add("Decompress")
        self.tab_view.add("Logs")

        self._create_compress_tab(self.tab_view.tab("Compress"))
        self._create_decompress_tab(self.tab_view.tab("Decompress"))
        self._create_logs_tab(self.tab_view.tab("Logs"))

        self.progress_bar = ctk.CTkProgressBar(self, mode='indeterminate')
        self.status_label = ctk.CTkLabel(self, text="Status: Idle", anchor="w", height=20)
        self.status_label.pack(padx=10, pady=(0, 10), fill="x", side="bottom")

        self.update_log_display()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _create_compress_tab(self, tab):
        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Select File to Compress:").grid(row=0, column=0, padx=5, pady=(5, 10), sticky="w")
        ctk.CTkEntry(frame, textvariable=self.input_compress_path, width=350).grid(row=0, column=1, padx=5,
                                                                                   pady=(5, 10), sticky="ew")
        self.btn_browse_compress_in = ctk.CTkButton(frame, text="Browse", command=self._select_input_compress)
        self.btn_browse_compress_in.grid(row=0, column=2, padx=5, pady=(5, 10))
        ctk.CTkLabel(frame, text="Save Compressed File As:").grid(row=1, column=0, padx=5, pady=(5, 10), sticky="w")
        ctk.CTkEntry(frame, textvariable=self.output_compress_path, width=350).grid(row=1, column=1, padx=5,
                                                                                    pady=(5, 10), sticky="ew")
        self.btn_browse_compress_out = ctk.CTkButton(frame, text="Browse", command=self._select_output_compress)
        self.btn_browse_compress_out.grid(row=1, column=2, padx=5, pady=(5, 10))
        self.btn_compress = ctk.CTkButton(frame, text="Compress", command=self._compress_action, height=35)
        self.btn_compress.grid(row=2, column=0, columnspan=3, padx=5, pady=20)
        frame.grid_columnconfigure(1, weight=1)

    def _create_decompress_tab(self, tab):
        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        ctk.CTkLabel(frame, text=f"Select {COMPRESSED_EXTENSION} File to Decompress:").grid(row=0, column=0, padx=5,
                                                                                            pady=(5, 10), sticky="w")
        ctk.CTkEntry(frame, textvariable=self.input_decompress_path, width=350).grid(row=0, column=1, padx=5,
                                                                                     pady=(5, 10), sticky="ew")
        self.btn_browse_decompress_in = ctk.CTkButton(frame, text="Browse", command=self._select_input_decompress)
        self.btn_browse_decompress_in.grid(row=0, column=2, padx=5, pady=(5, 10))
        ctk.CTkLabel(frame, text="Save Decompressed File As:").grid(row=1, column=0, padx=5, pady=(5, 10), sticky="w")
        ctk.CTkEntry(frame, textvariable=self.output_decompress_path, width=350).grid(row=1, column=1, padx=5,
                                                                                      pady=(5, 10), sticky="ew")
        self.btn_browse_decompress_out = ctk.CTkButton(frame, text="Browse", command=self._select_output_decompress)
        self.btn_browse_decompress_out.grid(row=1, column=2, padx=5, pady=(5, 10))
        self.btn_decompress = ctk.CTkButton(frame, text="Decompress", command=self._decompress_action, height=35)
        self.btn_decompress.grid(row=2, column=0, columnspan=3, padx=5, pady=20)
        frame.grid_columnconfigure(1, weight=1)

    def _create_logs_tab(self, tab):
        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.log_textbox = ctk.CTkTextbox(frame, wrap="word", state="disabled")
        self.log_textbox.pack(padx=5, pady=5, fill="both", expand=True)
        self.btn_refresh_logs = ctk.CTkButton(frame, text="Refresh Logs", command=self.update_log_display)
        self.btn_refresh_logs.pack(pady=(10, 0))

    def update_log_display(self):
        if hasattr(self, 'log_textbox'):
            log_content = get_log_content()
            self.log_textbox.configure(state="normal")
            current_pos = self.log_textbox.yview()
            self.log_textbox.delete("1.0", "end")
            self.log_textbox.insert("1.0", log_content)
            self.log_textbox.yview_moveto(current_pos[0])
            if current_pos[1] > 0.95:
                self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")

    def _set_buttons_state(self, state):
        buttons = [
            self.btn_compress, self.btn_decompress,
            self.btn_browse_compress_in, self.btn_browse_compress_out,
            self.btn_browse_decompress_in, self.btn_browse_decompress_out,
            self.btn_refresh_logs
        ]
        for btn in buttons:
            if hasattr(btn, 'configure'):  # Check if button has been initialized
                btn.configure(state=state)

    def _task_started(self):
        with self.lock:
            self.active_threads += 1
        logging.info(f"Task started. Active threads: {self.active_threads}")
        self._set_buttons_state("disabled")
        self.progress_bar.pack(padx=10, pady=(5, 2), fill="x", side="bottom", before=self.status_label)
        self.progress_bar.start()

    def _task_finished(self, status_msg):
        with self.lock:
            self.active_threads -= 1
        logging.info(f"Task finished callback. Active threads: {self.active_threads}. Status: {status_msg}")
        if self.active_threads == 0:
            self._set_buttons_state("normal")
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
        self._update_status(status_msg)
        self.update_log_display()

    def _update_status(self, message):
        self.status_label.configure(text=f"Status: {message}")
        default_text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        if "error" in message.lower() or "failed" in message.lower() or "missing" in message.lower() or "corrupt" in message.lower():
            self.status_label.configure(text_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][1])
        elif "success" in message.lower():
            self.status_label.configure(text_color="green")
        else:
            self.status_label.configure(text_color=default_text_color)
        self.update_idletasks()

    def _run_task_in_thread(self, task_func, initial_status_msg, *args):
        logging.info(f"Preparing to run task '{task_func.__name__}' in a new thread.")
        self._update_status(initial_status_msg)
        self._task_started()

        def on_task_complete_status_update_wrapper(final_status_msg):
            self.after(0, self._task_finished, final_status_msg)

        def on_log_view_update_wrapper():
            self.after(0, self.update_log_display)

        thread = threading.Thread(target=task_func, name=task_func.__name__,
                                  args=args + (on_task_complete_status_update_wrapper, on_log_view_update_wrapper))
        thread.daemon = True
        thread.start()
        logging.info(f"Thread '{thread.name}' started for task with initial status: '{initial_status_msg}'.")

    def _select_input_compress(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            logging.info(f"Input file for compression selected: {filepath}")
            self.input_compress_path.set(filepath)
            suggested_output = filepath + COMPRESSED_EXTENSION
            self.output_compress_path.set(suggested_output)
            logging.info(f"Suggested output for compression: {suggested_output}")

    def _select_output_compress(self):
        current_suggestion = self.output_compress_path.get()
        directory = os.path.dirname(current_suggestion) if current_suggestion else "."
        filename = os.path.basename(current_suggestion) if current_suggestion else f"compressed{COMPRESSED_EXTENSION}"
        filepath = filedialog.asksaveasfilename(initialdir=directory, initialfile=filename,
                                                defaultextension=COMPRESSED_EXTENSION,
                                                filetypes=[(f"LZMA compressed files", f"*{COMPRESSED_EXTENSION}"),
                                                           ("All files", "*.*")])
        if filepath:
            logging.info(f"Output file for compression selected/set: {filepath}")
            self.output_compress_path.set(filepath)

    def _compress_action(self):
        in_path = self.input_compress_path.get()
        out_path = self.output_compress_path.get()
        logging.info(f"Compress action triggered. Input: '{in_path}', Output: '{out_path}'.")
        if not in_path:
            logging.warning("Compress action: Input file not selected.")
            messagebox.showerror("Error", "Please select an input file for compression.")
            return
        if not out_path:
            logging.warning("Compress action: Output file not specified.")
            messagebox.showerror("Error", "Please specify an output file for compression.")
            return
        if not os.path.exists(in_path):
            logging.error(f"Compress action: Input file not found at '{in_path}'.")
            messagebox.showerror("Error", f"Input file not found: {in_path}")
            return

        initial_msg = f"Compressing {os.path.basename(in_path)}..."
        self._run_task_in_thread(compress_file_task, initial_msg, in_path, out_path)

    def _select_input_decompress(self):
        filepath = filedialog.askopenfilename(
            filetypes=[(f"LZMA compressed files", f"*{COMPRESSED_EXTENSION}"), ("All files", "*.*")])
        if filepath:
            logging.info(f"Input file for decompression selected: {filepath}")
            self.input_decompress_path.set(filepath)
            base, ext = os.path.splitext(filepath)
            if ext.lower() == COMPRESSED_EXTENSION:
                suggested_output = base
                self.output_decompress_path.set(suggested_output)
                logging.info(f"Suggested output for decompression (removed .lzma): {suggested_output}")
            else:
                suggested_output = os.path.join(os.path.dirname(filepath),
                                                os.path.basename(base) + ext + ".decompressed")
                self.output_decompress_path.set(suggested_output)
                logging.info(f"Suggested output for decompression (unknown extension): {suggested_output}")

    def _select_output_decompress(self):
        current_suggestion = self.output_decompress_path.get()
        directory = os.path.dirname(current_suggestion) if current_suggestion else "."
        filename = os.path.basename(current_suggestion) if current_suggestion else "decompressed_file"
        filepath = filedialog.asksaveasfilename(initialdir=directory, initialfile=filename,
                                                filetypes=[("All files", "*.*")])
        if filepath:
            logging.info(f"Output file for decompression selected/set: {filepath}")
            self.output_decompress_path.set(filepath)

    def _decompress_action(self):
        in_path = self.input_decompress_path.get()
        out_path = self.output_decompress_path.get()
        logging.info(f"Decompress action triggered. Input: '{in_path}', Output: '{out_path}'.")
        if not in_path:
            logging.warning("Decompress action: Input file not selected.")
            messagebox.showerror("Error", "Please select an input file for decompression.")
            return
        if not out_path:
            logging.warning("Decompress action: Output file not specified.")
            messagebox.showerror("Error", "Please specify an output file for decompression.")
            return
        if not os.path.exists(in_path):
            logging.error(f"Decompress action: Input file not found at '{in_path}'.")
            messagebox.showerror("Error", f"Input file not found: {in_path}")
            return

        initial_msg = f"Decompressing {os.path.basename(in_path)}..."
        self._run_task_in_thread(decompress_file_task, initial_msg, in_path, out_path)

    def on_closing(self):
        logging.info("Application closing sequence initiated.")
        if self.active_threads > 0:
            logging.warning(f"Attempting to close application with {self.active_threads} active threads.")
            if messagebox.askokcancel("Quit",
                                      "Operations are still in progress. Are you sure you want to quit? Some data might be lost if operations are interrupted."):
                logging.info("User confirmed close while tasks active. Shutting down.")
                try:
                    super().destroy()  # Use super().destroy()
                except tkinter.TclError as e:
                    logging.error(f"TclError during destroy on confirmed quit: {e}. App likely already destroyed.")
                return  # Exit after destroy to prevent second destroy call or further processing
            else:
                logging.info("User cancelled application close due to active tasks.")
                return  # Do not close

        logging.info("Application closed gracefully.")
        try:
            super().destroy()  # Normal destroy
        except tkinter.TclError as e:
            logging.error(f"TclError during final destroy: {e}. App likely already destroyed by other means.")


if __name__ == "__main__":
    # Set the name of the main thread for logging clarity before app starts
    threading.current_thread().name = "MainThread"
    app = App()
    app.mainloop()