"""
Réalisé avec l'appui du GenAI pour la conception graphique.

TODO
"""

import os
import shlex
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk


class ParametersGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Energy Production Optimization")
        self.root.geometry("780x620")
        self.root.minsize(760, 560)

        self._build_style()
        self._build_variables()
        self._build_layout()

        self.worker = None
        self.process = None

    def _build_style(self):
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("SubTitle.TLabel", font=("Segoe UI", 10), foreground="#4a5568")
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))

    def _build_variables(self):
        self.data_file_var = tk.StringVar()
        self.version_var = tk.StringVar(value="1")
        self.time_limit_var = tk.StringVar(value="30")
        self.verbose_var = tk.BooleanVar(value=False)
        self.solution_folder_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")

    def _build_layout(self):
        outer = ttk.Frame(self.root, padding=14)
        outer.pack(fill=tk.BOTH, expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(2, weight=1)

        header = ttk.Frame(outer)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Energy Production Optimization", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text="Run solver.py with validated inputs and inspect logs in real time.",
            style="SubTitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 10))

        controls = ttk.LabelFrame(outer, text="Execution Parameters", style="Section.TLabelframe")
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        controls.columnconfigure(1, weight=1)

        ttk.Label(controls, text="Data File *").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.data_file_entry = ttk.Entry(controls, textvariable=self.data_file_var)
        self.data_file_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=8)
        self.browse_data_btn = ttk.Button(controls, text="Browse", command=self.browse_data_file)
        self.browse_data_btn.grid(row=0, column=2, padx=(0, 10), pady=8)

        ttk.Label(controls, text="Version *").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.version_combo = ttk.Combobox(
            controls,
            textvariable=self.version_var,
            values=["1", "2"],
            state="readonly",
            width=8,
        )
        self.version_combo.grid(row=1, column=1, sticky="w", pady=8)

        ttk.Label(controls, text="Time Limit (seconds)").grid(
            row=2, column=0, sticky="w", padx=10, pady=8
        )
        self.time_limit_entry = ttk.Entry(controls, textvariable=self.time_limit_var, width=12)
        self.time_limit_entry.grid(row=2, column=1, sticky="w", pady=8)

        self.verbose_check = ttk.Checkbutton(
            controls,
            text="Verbose output (-p)",
            variable=self.verbose_var,
        )
        self.verbose_check.grid(row=3, column=1, sticky="w", pady=8)

        ttk.Label(controls, text="Solution Folder").grid(row=4, column=0, sticky="w", padx=10, pady=8)
        self.solution_folder_entry = ttk.Entry(controls, textvariable=self.solution_folder_var)
        self.solution_folder_entry.grid(row=4, column=1, sticky="ew", padx=(0, 8), pady=8)
        self.browse_folder_btn = ttk.Button(
            controls, text="Browse", command=self.browse_solution_folder
        )
        self.browse_folder_btn.grid(row=4, column=2, padx=(0, 10), pady=8)

        log_frame = ttk.LabelFrame(outer, text="Execution Log", style="Section.TLabelframe")
        log_frame.grid(row=2, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state=tk.DISABLED,
            height=14,
        )
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        footer = ttk.Frame(outer)
        footer.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        footer.columnconfigure(1, weight=1)

        self.run_btn = ttk.Button(footer, text="Run", command=self.run)
        self.run_btn.grid(row=0, column=0, padx=(0, 8))
        self.reset_btn = ttk.Button(footer, text="Reset", command=self.reset)
        self.reset_btn.grid(row=0, column=1, sticky="w")
        self.exit_btn = ttk.Button(footer, text="Exit", command=self.exit_app)
        self.exit_btn.grid(row=0, column=2, padx=(8, 0))

        status_frame = ttk.Frame(outer)
        status_frame.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        status_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=0, sticky="w")
        self.progress = ttk.Progressbar(status_frame, mode="indeterminate", length=180)
        self.progress.grid(row=0, column=1, sticky="e")

    def browse_data_file(self):
        filename = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if filename:
            self.data_file_var.set(filename)

    def browse_solution_folder(self):
        folder = filedialog.askdirectory(title="Select Solution Folder")
        if folder:
            self.solution_folder_var.set(folder)

    def validate_inputs(self):
        errors = []

        data_file = self.data_file_var.get().strip()
        if not data_file:
            errors.append("Data file is required.")
        elif not os.path.isfile(data_file):
            errors.append(f"Data file not found: {data_file}")

        version = self.version_var.get().strip()
        if version not in {"1", "2"}:
            errors.append("Version must be 1 or 2.")

        try:
            time_limit = int(self.time_limit_var.get().strip())
            if time_limit <= 0:
                errors.append("Time limit must be a positive integer.")
        except ValueError:
            errors.append("Time limit must be an integer.")

        folder = self.solution_folder_var.get().strip()
        if folder:
            try:
                os.makedirs(folder, exist_ok=True)
            except OSError as exc:
                errors.append(f"Cannot create/access solution folder '{folder}': {exc}")

        return errors

    def _append_log(self, text):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _set_busy(self, busy):
        widgets = [
            self.data_file_entry,
            self.version_combo,
            self.time_limit_entry,
            self.solution_folder_entry,
            self.browse_data_btn,
            self.browse_folder_btn,
            self.run_btn,
            self.reset_btn,
            self.verbose_check,
        ]
        state = tk.DISABLED if busy else tk.NORMAL
        for widget in widgets:
            widget.configure(state=state)
        self.version_combo.configure(state="disabled" if busy else "readonly")

        if busy:
            self.progress.start(10)
        else:
            self.progress.stop()

    def _build_command(self):
        solver_script = os.path.join(os.path.dirname(__file__), "solver.py")
        cmd = [
            sys.executable,
            solver_script,
            "-d",
            self.data_file_var.get().strip(),
            "-v",
            self.version_var.get().strip(),
            "-t",
            self.time_limit_var.get().strip(),
        ]

        if self.verbose_var.get():
            cmd.append("-p")

        solution_folder = self.solution_folder_var.get().strip()
        if solution_folder:
            cmd.extend(["-f", solution_folder])

        return cmd

    def run(self):
        if self.worker and self.worker.is_alive():
            messagebox.showwarning("Execution Running", "A solver run is already in progress.")
            return

        errors = self.validate_inputs()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        cmd = self._build_command()
        display_cmd = " ".join(shlex.quote(part) for part in cmd)

        self._append_log("\n=== New execution ===\n")
        self._append_log(f"Command: {display_cmd}\n\n")
        self.status_var.set("Running solver...")
        self._set_busy(True)

        self.worker = threading.Thread(target=self._run_process, args=(cmd,), daemon=True)
        self.worker.start()

    def _run_process(self, cmd):
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            if self.process.stdout is not None:
                for line in self.process.stdout:
                    self.root.after(0, self._append_log, line)

            return_code = self.process.wait()
            self.root.after(0, self._on_process_done, return_code)

        except Exception as exc:
            self.root.after(0, self._on_process_error, exc)

    def _on_process_done(self, return_code):
        self.process = None
        self._set_busy(False)

        if return_code == 0:
            self.status_var.set("Completed successfully")
            self._append_log("\nExecution finished successfully.\n")
            messagebox.showinfo("Success", "Solver execution completed successfully.")
            return

        self.status_var.set(f"Failed (return code {return_code})")
        self._append_log(f"\nExecution failed with return code {return_code}.\n")
        messagebox.showerror("Execution Error", f"Solver failed with return code {return_code}.")

    def _on_process_error(self, exc):
        self.process = None
        self._set_busy(False)
        self.status_var.set("Execution error")
        self._append_log(f"\nUnexpected error: {exc}\n")
        messagebox.showerror("Execution Error", str(exc))

    def reset(self):
        if self.worker and self.worker.is_alive():
            messagebox.showwarning("Execution Running", "Wait until execution finishes before reset.")
            return

        self.data_file_var.set("")
        self.version_var.set("1")
        self.time_limit_var.set("30")
        self.verbose_var.set(False)
        self.solution_folder_var.set("")
        self.status_var.set("Ready")

        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def exit_app(self):
        if self.process and self.process.poll() is None:
            should_close = messagebox.askyesno(
                "Execution Running",
                "A solver process is still running. Close the GUI anyway?",
            )
            if not should_close:
                return
        self.root.quit()
        self.root.destroy()
        sys.exit(0)


def gui_main():
    root = tk.Tk()
    ParametersGUI(root)
    root.mainloop()

if __name__ == "__main__":
    gui_main()
