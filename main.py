import os
import csv
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scanner import FileScanner
from duplicate_detector import DuplicateDetector
from storage_analyzer import StorageAnalyzer
from file_type_analyzer import FileTypeAnalyzer
from duplicate_priority import DuplicatePriorityAnalyzer
from database import DatabaseManager
from quarantine import QuarantineManager
from report_generator import ReportGenerator
from ram_monitor import RAMMonitor

import matplotlib.pyplot as plt


class SmartDeduplicationApp:

    def __init__(self, root):

        self.root = root
        self.root.title(
            "Smart Data Deduplication and Storage Optimization System"
        )
        self.root.geometry("1280x820")
        self.root.minsize(1150, 750)

     # ===== PROFESSIONAL COLOUR THEME =====
        self.bg = "#F1F5F9"       # Main background
        self.header = "#172554"   # Deep navy header
        self.blue = "#2563EB"     # Primary blue
        self.green = "#059669"    # Success green
        self.red = "#DC2626"      # Error red
        self.orange = "#D97706"   # Warning orange
        self.purple = "#7C3AED"   # Analytics purple
        self.cyan = "#0891B2"     # Information cyan
        self.dark = "#0F172A"     # Dark text
        self.white = "#FFFFFF"    # White cards

        self.root.configure(bg=self.bg)

        self.scanner = FileScanner()
        self.duplicate_detector = DuplicateDetector()
        self.storage_analyzer = StorageAnalyzer()
        self.file_type_analyzer = FileTypeAnalyzer()
        self.priority_analyzer = DuplicatePriorityAnalyzer()
        self.database = DatabaseManager()
        self.quarantine_manager = QuarantineManager()
        self.report_generator = ReportGenerator()
        self.ram_monitor = RAMMonitor()

        self.selected_folder = ""
        self.files = []
        self.duplicate_groups = []
        self.priority_results = []
        self.folder_analysis = {}
        self.extension_analysis = {}

        self.storage_wasted = 0
        self.potential_saving = 0
        self.saving_percentage = 0
        self.scan_time = 0

        self.ram_before = 0
        self.ram_peak = 0
        self.ram_after = 0

        self.scanning = False
                # Scan control and live progress
        self.stop_event = threading.Event()
        self.processed_count = 0
        self.create_style()
        self.create_layout()
    # ---------------------------------------------------------
    # PROFESSIONAL STYLE
    # ---------------------------------------------------------

    def create_style(self):

        style = ttk.Style()

        # Use a theme that supports custom colours
        style.theme_use("clam")

        # ===== GENERAL COLOURS =====
        style.configure(
            ".",
            font=("Segoe UI", 10)
        )

        # ===== TABLE STYLE =====
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground=self.dark,
            fieldbackground="#FFFFFF",
            rowheight=34,
            font=("Segoe UI", 10),
            borderwidth=0,
            relief="flat"
        )

        # Table heading
        style.configure(
            "Treeview.Heading",
            background=self.header,
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            padding=[10, 10],
            relief="flat",
            borderwidth=0
        )

        # Table hover and selected-row colours
        style.map(
            "Treeview",
            background=[
                ("selected", "#DBEAFE")
            ],
            foreground=[
                ("selected", "#1E3A8A")
            ]
        )

        # ===== NOTEBOOK / TABS =====
        style.configure(
            "TNotebook",
            background=self.bg,
            borderwidth=0,
            tabmargins=[4, 4, 4, 0]
        )

        style.configure(
            "TNotebook.Tab",
            background="#E2E8F0",
            foreground="#475569",
            padding=[16, 10],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0
        )

        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", self.blue),
                ("active", "#BFDBFE")
            ],
            foreground=[
                ("selected", "#FFFFFF"),
                ("active", "#1E3A8A")
            ]
        )

        # ===== BUTTONS =====
        style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=[12, 8],
            background=self.blue,
            foreground="#FFFFFF",
            borderwidth=0,
            relief="flat"
        )

        style.map(
            "TButton",
            background=[
                ("disabled", "#CBD5E1"),
                ("pressed", "#1D4ED8"),
                ("active", "#1D4ED8")
            ],
            foreground=[
                ("disabled", "#64748B"),
                ("!disabled", "#FFFFFF")
            ]
        )

        # ===== INPUT FIELDS =====
        style.configure(
            "TEntry",
            fieldbackground="#FFFFFF",
            foreground=self.dark,
            padding=[8, 7],
            borderwidth=1
        )

        style.map(
            "TEntry",
            fieldbackground=[
                ("disabled", "#F1F5F9"),
                ("!disabled", "#FFFFFF")
            ]
        )

        # ===== DROPDOWN =====
        style.configure(
            "TCombobox",
            fieldbackground="#FFFFFF",
            background="#E2E8F0",
            foreground=self.dark,
            padding=[8, 7],
            arrowsize=15
        )

        style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", "#FFFFFF")
            ],
            foreground=[
                ("readonly", self.dark)
            ],
            selectbackground=[
                ("readonly", "#DBEAFE")
            ],
            selectforeground=[
                ("readonly", self.dark)
            ]
        )

        # ===== PROGRESS BAR =====
        style.configure(
            "Horizontal.TProgressbar",
            troughcolor="#E2E8F0",
            background=self.blue,
            bordercolor="#E2E8F0",
            lightcolor=self.blue,
            darkcolor=self.blue,
            thickness=12
        )

        # ===== SCROLLBAR =====
        style.configure(
            "Vertical.TScrollbar",
            background="#CBD5E1",
            troughcolor=self.bg,
            borderwidth=0,
            arrowsize=12
        )

        style.map(
            "Vertical.TScrollbar",
            background=[
                ("active", "#94A3B8")
            ]
        )
        # ---------------------------------------------------------
    # MAIN LAYOUT - PROFESSIONAL DESIGN
    # ---------------------------------------------------------

    def create_layout(self):

        # ===== TOP HEADER =====
        header = tk.Frame(
            self.root,
            bg=self.header,
            height=75
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        # Application title
        tk.Label(
            header,
            text="Smart Data Deduplication",
            font=("Segoe UI", 22, "bold"),
            fg="#FFFFFF",
            bg=self.header
        ).pack(
            side="left",
            padx=(25, 12),
            pady=15
        )

        # Application subtitle
        tk.Label(
            header,
            text="Storage Optimization System",
            font=("Segoe UI", 11),
            fg="#CBD5E1",
            bg=self.header
        ).pack(
            side="left",
            pady=22
        )

        # ===== MAIN CONTAINER =====
        main_frame = tk.Frame(
            self.root,
            bg=self.bg
        )
        main_frame.pack(
            fill="both",
            expand=True
        )

        # ===== SIDEBAR =====
        sidebar = tk.Frame(
            main_frame,
            bg="#FFFFFF",
            width=220,
            highlightbackground="#E2E8F0",
            highlightthickness=1
        )
        sidebar.pack(
            side="left",
            fill="y"
        )
        sidebar.pack_propagate(False)

        # Create existing navigation buttons
        self.create_sidebar(sidebar)

        # ===== MAIN CONTENT AREA =====
        content = tk.Frame(
            main_frame,
            bg=self.bg
        )
        content.pack(
            side="left",
            fill="both",
            expand=True,
            padx=0,
            pady=0
        )

        # Load the existing dashboard
        self.create_dashboard(content)

        # ---------------------------------------------------------
    # SIDEBAR - PROFESSIONAL DESIGN
    # ---------------------------------------------------------

    def create_sidebar(self, parent):

        # Sidebar heading
        tk.Label(
            parent,
            text="PROJECT MENU",
            font=("Segoe UI", 10, "bold"),
            fg="#64748B",
            bg="#FFFFFF"
        ).pack(
            anchor="w",
            padx=20,
            pady=(25, 12)
        )

        # Navigation buttons
        self.sidebar_button(
            parent, "📁 Select Folder",
            self.select_folder, "#2563EB"
        )

        self.sidebar_button(
            parent, "🔍 Start Scan",
            self.start_scan, "#059669"
        )

        self.sidebar_button(
            parent, "📊 Analysis",
            self.show_analysis, "#6D5AE6"
        )

        self.sidebar_button(
            parent, "♻ Duplicate Groups",
            self.show_duplicates, "#D97706"
        )

        self.sidebar_button(
            parent, "🕒 Scan History",
            self.show_history, "#0891B2"
        )

        self.sidebar_button(
            parent, "📄 Generate Reports",
            self.generate_reports, "#DC2626"
        )

        self.sidebar_button(
            parent, "📂 View Reports",
            self.open_report_manager, "#0284C7"
        )

        self.sidebar_button(
            parent, "🛡 Quarantine Manager",
            self.open_quarantine_manager, "#B45309"
        )

        self.sidebar_button(
            parent, "📈 Graphs",
            self.show_graphs, "#7C3AED"
        )

        # Divider
        tk.Frame(
            parent,
            bg="#E2E8F0",
            height=1
        ).pack(
            fill="x",
            padx=15,
            pady=18
        )

        # Selected folder heading
        tk.Label(
            parent,
            text="SELECTED FOLDER",
            font=("Segoe UI", 9, "bold"),
            fg="#64748B",
            bg="#FFFFFF"
        ).pack(
            anchor="w",
            padx=20
        )

        # Selected folder path
        self.folder_label = tk.Label(
            parent,
            text="No folder selected",
            font=("Segoe UI", 9),
            fg="#334155",
            bg="#FFFFFF",
            wraplength=180,
            justify="left",
            anchor="w"
        )

        self.folder_label.pack(
            anchor="w",
            fill="x",
            padx=20,
            pady=8
        )

    # ---------------------------------------------------------
    # SIDEBAR BUTTON - PROFESSIONAL STYLE
    # ---------------------------------------------------------

    def sidebar_button(
        self,
        parent,
        text,
        command,
        color
    ):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="#FFFFFF",
            activebackground="#1E40AF",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            anchor="w",
            padx=15,
            pady=2,
            highlightthickness=0
        )

        button.pack(
            fill="x",
            padx=15,
            pady=4,
            ipady=6
        )

        # Hover effect
        button.bind(
            "<Enter>",
            lambda event, b=button: b.configure(
                bg="#1E293B"
            )
        )

        button.bind(
            "<Leave>",
            lambda event, b=button, c=color: b.configure(
                bg=c
            )
        )
        # ---------------------------------------------------------
    # DASHBOARD - PROFESSIONAL DESIGN
    # ---------------------------------------------------------

    def create_dashboard(self, parent):

        # ===== DASHBOARD HEADER =====
        top = tk.Frame(
            parent,
            bg=self.bg
        )
        top.pack(
            fill="x",
            padx=24,
            pady=(24, 18)
        )

        tk.Label(
            top,
            text="Dashboard",
            font=("Segoe UI", 24, "bold"),
            bg=self.bg,
            fg="#0F172A"
        ).pack(side="left")

        self.status_label = tk.Label(
            top,
            text="● Ready",
            font=("Segoe UI", 10, "bold"),
            fg="#059669",
            bg=self.bg
        )
        self.status_label.pack(side="right")

        # ===== FOLDER SELECTION PANEL =====
        folder_frame = tk.Frame(
            parent,
            bg="#FFFFFF",
            highlightbackground="#E2E8F0",
            highlightthickness=1
        )
        folder_frame.pack(
            fill="x",
            padx=24,
            pady=(0, 18)
        )

        self.folder_entry = tk.Entry(
            folder_frame,
            font=("Segoe UI", 11),
            bg="#F8FAFC",
            fg="#334155",
            insertbackground="#2563EB",
            relief="flat",
            bd=0
        )
        self.folder_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(14, 8),
            pady=14,
            ipady=9
        )

        tk.Button(
            folder_frame,
            text="Browse Folder",
            command=self.select_folder,
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=16,
            pady=9
        ).pack(
            side="right",
            padx=(4, 12),
            pady=10
        )

      #  tk.Button(
       #    activeforeground="#FFFFFF",
        #    relief="flat",
         #   bd=0,
          #  font=("Segoe UI", 10, "bold"),
           # cursor="hand2",
            #padx=14,
            #pady=9
        #).pack(
         #   side="right",
          #  padx=4,
           # pady=10
        #)

        # ===== SCAN PROGRESS =====
        self.progress = ttk.Progressbar(
            parent,
            mode="indeterminate"
        )
        self.progress.pack(
            fill="x",
            padx=24,
            pady=(0, 20)
        )
                # ===== LIVE SCAN COUNTER =====
        scan_control_frame = tk.Frame(
            parent,
            bg=self.bg
        )
        scan_control_frame.pack(
            fill="x",
            padx=24,
            pady=(0, 15)
        )

        self.scan_counter_label = tk.Label(
            scan_control_frame,
            text="Files Scanned: 0",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg,
            fg=self.dark
        )
        self.scan_counter_label.pack(side="left")

        self.stop_button = tk.Button(
            scan_control_frame,
            text="Stop Scanning",
            command=self.stop_scan,
            bg=self.red,
            fg=self.white,
            activebackground="#B91C1C",
            activeforeground=self.white,
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=16,
            pady=7,
            state="disabled"
        )
        self.stop_button.pack(side="right")
        # ===== STATISTICS CARDS =====
        cards = tk.Frame(
            parent,
            bg=self.bg
        )
        cards.pack(
            fill="x",
            padx=20,
            pady=(0, 8)
        )

        self.card_total = self.create_card(
            cards,
            "TOTAL FILES",
            "0",
            "#2563EB"
        )

        self.card_duplicates = self.create_card(
            cards,
            "DUPLICATE FILES",
            "0",
            "#DC2626"
        )

        self.card_wasted = self.create_card(
            cards,
            "WASTED STORAGE",
            "0 B",
            "#D97706"
        )

        self.card_saving = self.create_card(
            cards,
            "POTENTIAL SAVING",
            "0 B",
            "#059669"
        )

        for card in (
            self.card_total,
            self.card_duplicates,
            self.card_wasted,
            self.card_saving
        ):
            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=5,
                pady=5
            )

        # ===== SCAN INFORMATION =====
        self.create_quick_info(parent)

    # ---------------------------------------------------------
    # DASHBOARD STATISTICS CARD
    # ---------------------------------------------------------

    def create_card(
        self,
        parent,
        title,
        value,
        color
    ):

        frame = tk.Frame(
            parent,
            bg="#FFFFFF",
            height=112,
            highlightbackground="#E2E8F0",
            highlightthickness=1
        )
        frame.pack_propagate(False)

        # Coloured accent strip
        tk.Frame(
            frame,
            bg=color,
            height=4
        ).pack(
            side="top",
            fill="x"
        )

        inner = tk.Frame(
            frame,
            bg="#FFFFFF"
        )
        inner.pack(
            fill="both",
            expand=True,
            padx=13,
            pady=10
        )

        tk.Label(
            inner,
            text=title,
            font=("Segoe UI", 9, "bold"),
            fg="#64748B",
            bg="#FFFFFF"
        ).pack(anchor="w")

        value_label = tk.Label(
            inner,
            text=value,
            font=("Segoe UI", 19, "bold"),
            fg="#0F172A",
            bg="#FFFFFF"
        )
        value_label.pack(
            anchor="w",
            pady=(7, 0)
        )

        # Preserve the existing value_label reference
        frame.value_label = value_label

        return frame

    # ---------------------------------------------------------
    # SCAN INFORMATION PANEL
    # ---------------------------------------------------------

    def create_quick_info(self, parent):

        info = tk.Frame(
            parent,
            bg="#FFFFFF",
            highlightbackground="#E2E8F0",
            highlightthickness=1
        )
        info.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=(12, 20)
        )

        tk.Label(
            info,
            text="Scan Information",
            font=("Segoe UI", 15, "bold"),
            bg="#FFFFFF",
            fg="#0F172A"
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        self.info_text = tk.Text(
            info,
            height=12,
            font=("Consolas", 10),
            bg="#F8FAFC",
            fg="#334155",
            insertbackground="#2563EB",
            selectbackground="#BFDBFE",
            selectforeground="#0F172A",
            relief="flat",
            wrap="word",
            padx=15,
            pady=12,
            borderwidth=0
        )
        self.info_text.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.set_info(
            "Select a folder and click Start Scan."
        )
        # ---------------------------------------------------------
    # FOLDER SELECTION - PROFESSIONAL DESIGN
    # ---------------------------------------------------------

    def select_folder(self):

        folder = filedialog.askdirectory(
            parent=self.root,
            title="Select Folder to Scan"
        )

        if not folder:
            return

        self.selected_folder = folder

        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, folder)

        self.folder_label.config(
            text=folder,
            fg="#1E293B"
        )

        self.set_status(
            "Folder selected",
            "#059669"
        )
            # ---------------------------------------------------------
    # STOP SCANNING
    # ---------------------------------------------------------

    def stop_scan(self):

        if self.scanning:
            self.stop_event.set()

            self.set_status(
                "Stopping Scan...",
                "#D97706"
            )

            self.set_info(
                "Stopping scan safely...\n\n"
                "Please wait while the current file operation finishes."
            )

    # ---------------------------------------------------------
    # LIVE SCAN PROGRESS
    # ---------------------------------------------------------

    def scan_progress_callback(self, progress_data):

        self.root.after(
            0,
            lambda data=progress_data:
            self.update_scan_progress(data)
        )

    def update_scan_progress(self, progress_data):

        processed = progress_data.get("processed", 0)

        self.processed_count = processed

        self.scan_counter_label.config(
            text=f"Files Scanned: {processed}"
        )
    # ---------------------------------------------------------
    # BACK TO DASHBOARD BUTTON
    # ---------------------------------------------------------

    def add_back_button(self, window):

        back_button = tk.Button(
            window,
            text="← Back to Dashboard",
            command=window.destroy,
            bg=self.blue,
            fg=self.white,
            activebackground="#1D4ED8",
            activeforeground=self.white,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=15,
            pady=8
        )

        back_button.pack(
            anchor="w",
            padx=20,
            pady=10
        )
    # ---------------------------------------------------------
    # AVAILABLE DRIVES
    # ---------------------------------------------------------

    def get_available_drives(self):
        """Return drive roots available on this computer."""

        drives = []

        if os.name == "nt":
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                drive = f"{letter}:\\"

                if os.path.exists(drive):
                    drives.append(drive)
        else:
            drives.append(os.path.abspath(os.sep))

        return drives

    # ---------------------------------------------------------
    # SELECT DRIVE - PROFESSIONAL DIALOG
    # ---------------------------------------------------------

    def select_drive(self):
        """Allow the user to choose a drive for scanning."""

        drives = self.get_available_drives()

        if not drives:
            messagebox.showinfo(
                "No Drives Found",
                "No available drive roots were found. "
                "Use Browse to select a folder.",
                parent=self.root
            )
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Select a Drive")
        dialog.geometry("420x230")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg="#F1F5F9")

        # Dialog heading
        tk.Label(
            dialog,
            text="Select Drive",
            font=("Segoe UI", 17, "bold"),
            bg="#F1F5F9",
            fg="#0F172A"
        ).pack(pady=(22, 5))

        tk.Label(
            dialog,
            text="Choose the drive you want to scan.",
            font=("Segoe UI", 10),
            bg="#F1F5F9",
            fg="#64748B"
        ).pack(pady=(0, 12))

        # Drive dropdown
        drive_var = tk.StringVar(value=drives[0])

        drive_combo = ttk.Combobox(
            dialog,
            textvariable=drive_var,
            values=drives,
            state="readonly",
            font=("Segoe UI", 11),
            width=25
        )
        drive_combo.pack(pady=5, ipady=3)

        # Confirm selection
        def choose():

            drive = drive_var.get().strip()

            if not drive or not os.path.isdir(drive):
                messagebox.showerror(
                    "Invalid Drive",
                    "Please choose an available drive.",
                    parent=dialog
                )
                return

            self.selected_folder = drive

            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, drive)

            self.folder_label.config(
                text=drive,
                fg="#1E293B"
            )

            self.set_status(
                "Drive selected",
                "#059669"
            )

            dialog.destroy()

        # Buttons panel
        buttons = tk.Frame(
            dialog,
            bg="#F1F5F9"
        )
        buttons.pack(pady=15)

        tk.Button(
            buttons,
            text="Cancel",
            command=dialog.destroy,
            bg="#E2E8F0",
            fg="#334155",
            activebackground="#CBD5E1",
            activeforeground="#0F172A",
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=18,
            pady=8
        ).pack(side="left", padx=6)

        tk.Button(
            buttons,
            text="Use This Drive",
            command=choose,
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=18,
            pady=8
        ).pack(side="left", padx=6)

        # ---------------------------------------------------------
    # SCANNING - IMPROVED STATUS AND ERROR HANDLING
    # ---------------------------------------------------------

    def start_scan(self):

        if self.scanning:
            return

        folder = self.folder_entry.get().strip()

        if not folder:
            messagebox.showwarning(
                "Folder Required",
                "Please select a folder before starting the scan.",
                parent=self.root
            )
            return

        if not os.path.isdir(folder):
            messagebox.showerror(
                "Invalid Folder",
                "The selected folder does not exist or is unavailable.",
                parent=self.root
            )
            return

        self.selected_folder = folder
        self.scanning = True
        # Reset scan controls
        self.stop_event.clear()
        self.processed_count = 0

        self.scan_counter_label.config(
            text="Files Scanned: 0"
        )

        self.stop_button.config(
            state="normal"
        )
        self.progress.start(10)

        self.set_status(
            "Scanning...",
            "#2563EB"
        )

        self.set_info(
            "SCAN IN PROGRESS\n\n"
            f"Selected Folder:\n{folder}\n\n"
            "Files are being scanned and duplicate hashes "
            "are being analyzed.\n\n"
            "Please wait until the scan is complete."
        )

        thread = threading.Thread(
            target=self.perform_scan,
            daemon=True
        )
        thread.start()

    def perform_scan(self):

        start_time = time.time()

        try:
            self.ram_monitor.start_monitoring()

            files = self.scanner.scan_folder(
                self.selected_folder,
                progress_callback=self.scan_progress_callback,
                stop_event=self.stop_event
            )

            self.ram_monitor.update_peak()

            duplicate_groups = (
                self.duplicate_detector.find_duplicates(files)
            )

            self.ram_monitor.update_peak()

            storage_wasted = (
                self.storage_analyzer.calculate_storage_wasted(
                    duplicate_groups
                )
            )

            potential_saving = (
                self.storage_analyzer.calculate_potential_saving(
                    duplicate_groups
                )
            )

            total_size = sum(
                file.get("size", 0)
                for file in files
            )

            saving_percentage = (
                self.storage_analyzer.calculate_saving_percentage(
                    total_size,
                    potential_saving
                )
            )

            folder_analysis = (
                self.scanner.get_folder_analysis()
            )

            extension_analysis = (
                self.file_type_analyzer.analyze_extensions(files)
            )

            priority_results = (
                self.priority_analyzer.analyze(duplicate_groups)
            )

            self.ram_monitor.update_peak()
            self.ram_monitor.stop_monitoring()

            scan_time = time.time() - start_time

            self.files = files
            self.duplicate_groups = duplicate_groups
            self.folder_analysis = folder_analysis
            self.extension_analysis = extension_analysis
            self.priority_results = priority_results

            self.storage_wasted = storage_wasted
            self.potential_saving = potential_saving
            self.saving_percentage = saving_percentage
            self.scan_time = scan_time

            self.ram_before = self.ram_monitor.get_ram_before()
            self.ram_peak = self.ram_monitor.get_ram_peak()
            self.ram_after = self.ram_monitor.get_ram_after()

            duplicate_files = (
                self.duplicate_detector.get_duplicate_file_count(
                    duplicate_groups
                )
            )

            skipped_files = self.scanner.get_skipped_count()

            self.database.save_scan(
                self.selected_folder,
                len(files),
                total_size,
                len(duplicate_groups),
                duplicate_files,
                storage_wasted,
                potential_saving,
                saving_percentage,
                skipped_files,
                scan_time
            )

            self.root.after(0, self.scan_completed)

        except Exception as error:

            # Attempt to stop RAM monitoring if scanning fails.
            try:
                self.ram_monitor.stop_monitoring()
            except Exception:
                pass

            error_message = str(error)

            self.root.after(
                0,
                lambda msg=error_message: self.scan_failed(msg)
            )

    def scan_completed(self):

        self.scanning = False
        self.progress.stop()
        self.stop_button.config(
            state="disabled"
        )
        self.update_cards()

        duplicate_files = (
            self.duplicate_detector.get_duplicate_file_count(
                self.duplicate_groups
            )
        )

        skipped = self.scanner.get_skipped_count()

        if self.scanner.get_is_stopped():

            self.set_status(
                "Scan Stopped",
                "#D97706"
            )

        else:

            self.set_status(
                "Scan Complete",
                "#059669"
            )

        self.set_info(
            f"SCAN COMPLETED SUCCESSFULLY\n\n"
            f"Folder: {self.selected_folder}\n\n"
            f"Total Files: {len(self.files)}\n"
            f"Duplicate Groups: {len(self.duplicate_groups)}\n"
            f"Duplicate Files: {duplicate_files}\n"
            f"Wasted Storage: "
            f"{self.storage_analyzer.format_size(self.storage_wasted)}\n"
            f"Potential Saving: "
            f"{self.storage_analyzer.format_size(self.potential_saving)}\n"
            f"Saving Percentage: {self.saving_percentage:.2f}%\n"
            f"Skipped Files: {skipped}\n"
            f"Scan Time: {self.scan_time:.2f} seconds\n\n"
            f"RAM Before: {self.ram_before:.2f}%\n"
            f"Peak RAM: {self.ram_peak:.2f}%\n"
            f"RAM After: {self.ram_after:.2f}%"
        )

        messagebox.showinfo(
            "Scan Complete",
            "Folder scanning and duplicate analysis completed.",
            parent=self.root
        )

    def scan_failed(self, error):

        self.scanning = False
        self.progress.stop()
        self.stop_button.config(
            state="disabled"
        )
        self.set_status(
            "Scan Failed",
            "#DC2626"
        )

        self.set_info(
            "SCAN FAILED\n\n"
            "The scan could not be completed.\n\n"
            f"Error details:\n{error}"
        )

        messagebox.showerror(
            "Scan Error",
            str(error),
            parent=self.root
        )

        # ---------------------------------------------------------
    # CARDS
    # ---------------------------------------------------------

    def update_cards(self):
        duplicate_files = (
            self.duplicate_detector.get_duplicate_file_count(
                self.duplicate_groups
            )
        )

        self.card_total.value_label.config(
            text=str(len(self.files))
        )

        self.card_duplicates.value_label.config(
            text=str(duplicate_files)
        )

        self.card_wasted.value_label.config(
            text=self.storage_analyzer.format_size(
                self.storage_wasted
            )
        )

        self.card_saving.value_label.config(
            text=self.storage_analyzer.format_size(
                self.potential_saving
            )
        )

    # ---------------------------------------------------------
    # ANALYSIS WINDOW
    # ---------------------------------------------------------

    def show_analysis(self):
        if not self.files:
            messagebox.showinfo(
                "No Scan",
                "Please scan a folder first.",
                parent=self.root
            )
            return

        window = tk.Toplevel(self.root)
        window.title("Storage and Folder Analysis")
        window.geometry("1100x700")
        window.minsize(900, 550)
        window.configure(bg=self.bg)
        self.add_back_button(window)
        # Window heading
        header = tk.Frame(
            window,
            bg=self.header,
            height=85
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Storage & Folder Analysis",
            bg=self.header,
            fg=self.white,
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w", padx=25, pady=(15, 2))

        tk.Label(
            header,
            text="Explore files, duplicate storage, file types and memory usage",
            bg=self.header,
            fg="#CBD5E1",
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=26)

        # Main content area
        content = tk.Frame(window, bg=self.bg)
        content.pack(fill="both", expand=True, padx=16, pady=16)

        notebook = ttk.Notebook(content)
        notebook.pack(fill="both", expand=True)

        folder_tab = tk.Frame(notebook, bg=self.white)
        contents_tab = tk.Frame(notebook, bg=self.white)
        extension_tab = tk.Frame(notebook, bg=self.white)
        priority_tab = tk.Frame(notebook, bg=self.white)
        ram_tab = tk.Frame(notebook, bg=self.white)

        notebook.add(folder_tab, text="  Folder Analysis  ")
        notebook.add(contents_tab, text="  Folder Contents  ")
        notebook.add(extension_tab, text="  File Types  ")
        notebook.add(priority_tab, text="  Priority  ")
        notebook.add(ram_tab, text="  RAM Usage  ")

        self.create_folder_tree(folder_tab)
        self.create_folder_explorer(contents_tab)
        self.create_extension_tree(extension_tab)
        self.create_priority_tree(priority_tab)
        self.create_ram_view(ram_tab)

    # ---------------------------------------------------------
    # ANALYSIS TABLE HELPER
    # ---------------------------------------------------------

    def create_analysis_table(self, parent, columns, headings, widths):
        table_frame = tk.Frame(parent, bg=self.white)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=14
        )

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        for column, heading in zip(columns, headings):
            tree.heading(column, text=heading)
            tree.column(
                column,
                width=widths.get(column, 130),
                anchor="w"
            )

        yscroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree.yview
        )

        xscroll = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=tree.xview
        )

        tree.configure(
            yscrollcommand=yscroll.set,
            xscrollcommand=xscroll.set
        )

        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        return tree

    # ---------------------------------------------------------
    # FOLDER ANALYSIS
    # ---------------------------------------------------------

    def create_folder_tree(self, parent):
        columns = (
            "folder",
            "files",
            "size",
            "duplicates",
            "wasted"
        )

        tree = self.create_analysis_table(
            parent,
            columns,
            [
                "Folder",
                "Files",
                "Total Size",
                "Duplicate Files",
                "Wasted Storage"
            ],
            {
                "folder": 300,
                "files": 100,
                "size": 150,
                "duplicates": 140,
                "wasted": 170
            }
        )

        duplicate_info = (
            self.storage_analyzer.get_folder_duplicate_analysis(
                self.duplicate_groups
            )
        )

        for folder, data in self.folder_analysis.items():
            folder_data = duplicate_info.get(folder, {})

            duplicate_count = folder_data.get("files", 0)
            wasted = folder_data.get("wasted_storage", 0)

            tree.insert(
                "",
                tk.END,
                values=(
                    folder,
                    data["files"],
                    self.storage_analyzer.format_size(data["size"]),
                    duplicate_count,
                    self.storage_analyzer.format_size(wasted)
                )
            )

    # ---------------------------------------------------------
    # FOLDER CONTENTS EXPLORER
    # ---------------------------------------------------------

    def create_folder_explorer(self, parent):
        toolbar = tk.Frame(parent, bg=self.white)
        toolbar.pack(fill="x", padx=14, pady=(14, 8))

        tk.Label(
            toolbar,
            text="Search:",
            bg=self.white,
            fg=self.dark,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 8))

        self.folder_search_var = tk.StringVar()

        search_entry = ttk.Entry(
            toolbar,
            textvariable=self.folder_search_var,
            font=("Segoe UI", 10)
        )
        search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        clear_button = tk.Button(
            toolbar,
            text="Clear Search",
            command=lambda: self.folder_search_var.set(""),
            bg=self.blue,
            fg=self.white,
            activebackground=self.header,
            activeforeground=self.white,
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=6
        )
        clear_button.pack(side="left")

        tk.Label(
            parent,
            text=(
                "Expand folders to view subfolders and files. "
                "The last column displays the complete file path."
            ),
            bg=self.white,
            fg="#64748B",
            font=("Segoe UI", 9),
            anchor="w"
        ).pack(fill="x", padx=14, pady=(0, 8))

        table_frame = tk.Frame(parent, bg=self.white)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=(0, 14)
        )

        columns = (
            "kind",
            "name",
            "files",
            "size",
            "duplicate",
            "path"
        )

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings"
        )

        self.folder_explorer_tree = tree

        headings = {
            "#0": "Folder / File",
            "kind": "Type",
            "name": "Name",
            "files": "Files Inside",
            "size": "Size",
            "duplicate": "Duplicate",
            "path": "Complete Path"
        }

        tree.heading("#0", text=headings["#0"])

        for column in columns:
            tree.heading(column, text=headings[column])

        tree.column("#0", width=220, minwidth=150)
        tree.column("kind", width=90, anchor="center")
        tree.column("name", width=180, minwidth=120)
        tree.column("files", width=100, anchor="center")
        tree.column("size", width=110, anchor="e")
        tree.column("duplicate", width=100, anchor="center")
        tree.column("path", width=450, minwidth=250)

        yscroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree.yview
        )

        xscroll = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=tree.xview
        )

        tree.configure(
            yscrollcommand=yscroll.set,
            xscrollcommand=xscroll.set
        )

        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.folder_search_var.trace_add(
            "write",
            lambda *_: self.populate_folder_explorer()
        )

        self.populate_folder_explorer()

    # ---------------------------------------------------------
    # POPULATE FOLDER EXPLORER
    # ---------------------------------------------------------

    def populate_folder_explorer(self):
        tree = getattr(self, "folder_explorer_tree", None)

        if tree is None:
            return

        for item_id in tree.get_children(""):
            tree.delete(item_id)

        if not self.files:
            return

        valid_paths = [
            os.path.abspath(file_info["path"])
            for file_info in self.files
            if file_info.get("path")
        ]

        if not valid_paths:
            return

        root_path = os.path.abspath(
            self.selected_folder or os.path.commonpath(valid_paths)
        )

        query = (
            self.folder_search_var.get().strip().casefold()
            if hasattr(self, "folder_search_var")
            else ""
        )

        duplicate_paths = set()

        for group in self.duplicate_groups:
            for duplicate_file in group.get("files", []):
                path = duplicate_file.get("path", "")

                if path:
                    duplicate_paths.add(
                        os.path.normcase(os.path.abspath(path))
                    )

        folder_stats = {}
        visible_files = []

        for file_info in self.files:
            file_path = file_info.get("path", "")

            if not file_path:
                continue

            file_path = os.path.abspath(file_path)

            try:
                relative_path = os.path.relpath(file_path, root_path)
            except ValueError:
                continue

            if relative_path == os.pardir or relative_path.startswith(
                os.pardir + os.sep
            ):
                continue

            parent_path = os.path.dirname(file_path)

            ancestor = parent_path

            while True:
                stats = folder_stats.setdefault(
                    ancestor,
                    {
                        "files": 0,
                        "size": 0,
                        "duplicates": 0
                    }
                )

                stats["files"] += 1
                stats["size"] += int(file_info.get("size", 0) or 0)

                normalized_file = os.path.normcase(file_path)

                if normalized_file in duplicate_paths:
                    stats["duplicates"] += 1

                if os.path.normcase(ancestor) == os.path.normcase(root_path):
                    break

                next_ancestor = os.path.dirname(ancestor)

                if next_ancestor == ancestor:
                    break

                try:
                    if os.path.commonpath(
                        [root_path, next_ancestor]
                    ) != root_path:
                        break
                except ValueError:
                    break

                ancestor = next_ancestor

            file_name = (
                file_info.get("name")
                or os.path.basename(file_path)
            )

            if (
                not query
                or query in file_path.casefold()
                or query in file_name.casefold()
            ):
                visible_files.append(file_info)

        # Identify folders needed to display matching files.
        visible_folder_paths = {os.path.normcase(root_path)}

        for file_info in visible_files:
            current = os.path.dirname(
                os.path.abspath(file_info["path"])
            )

            while True:
                visible_folder_paths.add(os.path.normcase(current))

                if os.path.normcase(current) == os.path.normcase(root_path):
                    break

                next_current = os.path.dirname(current)

                if next_current == current:
                    break

                try:
                    if os.path.commonpath(
                        [root_path, next_current]
                    ) != root_path:
                        break
                except ValueError:
                    break

                current = next_current

        root_name = (
            os.path.basename(os.path.normpath(root_path))
            or root_path
        )

        root_stats = folder_stats.get(
            root_path,
            {"files": 0, "size": 0, "duplicates": 0}
        )

        root_iid = tree.insert(
            "",
            tk.END,
            text=root_name,
            open=True,
            values=(
                "Drive/Root",
                root_name,
                root_stats["files"],
                self.storage_analyzer.format_size(root_stats["size"]),
                root_stats["duplicates"],
                root_path
            )
        )

        folder_iids = {
            os.path.normcase(root_path): root_iid
        }

        # Build the folder hierarchy.
        all_folder_paths = set(folder_stats.keys())
        all_folder_paths.discard(root_path)

        ordered_folders = sorted(
            [
                path for path in all_folder_paths
                if path and os.path.isdir(path)
            ],
            key=lambda path: (
                path.count(os.sep),
                path.casefold()
            )
        )

        for folder_path in ordered_folders:
            normalized = os.path.normcase(
                os.path.abspath(folder_path)
            )

            if query and normalized not in visible_folder_paths:
                continue

            parent_path = os.path.dirname(
                os.path.abspath(folder_path)
            )

            parent_iid = folder_iids.get(
                os.path.normcase(parent_path)
            )

            if parent_iid is None:
                continue

            stats = folder_stats.get(
                folder_path,
                {"files": 0, "size": 0, "duplicates": 0}
            )

            folder_name = os.path.basename(folder_path) or folder_path

            iid = tree.insert(
                parent_iid,
                tk.END,
                text=folder_name,
                open=False,
                values=(
                    "Folder",
                    folder_name,
                    stats["files"],
                    self.storage_analyzer.format_size(stats["size"]),
                    stats["duplicates"],
                    folder_path
                )
            )

            folder_iids[normalized] = iid

        # Display files under their immediate parent folder.
        for file_info in sorted(
            visible_files,
            key=lambda item: item.get("path", "").casefold()
        ):
            file_path = os.path.abspath(file_info.get("path", ""))

            parent_iid = folder_iids.get(
                os.path.normcase(os.path.dirname(file_path))
            )

            if parent_iid is None:
                continue

            file_name = (
                file_info.get("name")
                or os.path.basename(file_path)
            )

            is_duplicate = (
                os.path.normcase(file_path) in duplicate_paths
            )

            tree.insert(
                parent_iid,
                tk.END,
                text=file_name,
                values=(
                    "File",
                    file_name,
                    "—",
                    self.storage_analyzer.format_size(
                        int(file_info.get("size", 0) or 0)
                    ),
                    "Yes" if is_duplicate else "No",
                    file_path
                )
            )

        if query:
            tree.item(root_iid, open=True)

    # ---------------------------------------------------------
    # FILE TYPE ANALYSIS
    # ---------------------------------------------------------

    def create_extension_tree(self, parent):
        columns = (
            "extension",
            "category",
            "files",
            "size"
        )

        tree = self.create_analysis_table(
            parent,
            columns,
            ["Extension", "Category", "Total Files", "Total Size"],
            {
                "extension": 160,
                "category": 220,
                "files": 120,
                "size": 200
            }
        )

        sorted_data = sorted(
            self.extension_analysis.items(),
            key=lambda item: item[1]["size"],
            reverse=True
        )

        for extension, data in sorted_data:
            tree.insert(
                "",
                tk.END,
                values=(
                    extension,
                    data["category"],
                    data["count"],
                    self.storage_analyzer.format_size(data["size"])
                )
            )

    # ---------------------------------------------------------
    # DUPLICATE PRIORITY ANALYSIS
    # ---------------------------------------------------------

    def create_priority_tree(self, parent):
        columns = (
            "rank",
            "priority",
            "files",
            "wasted",
            "share"
        )

        tree = self.create_analysis_table(
            parent,
            columns,
            ["Rank", "Priority", "Duplicate Files", "Wasted Storage", "Waste Share"],
            {
                "rank": 100,
                "priority": 180,
                "files": 150,
                "wasted": 200,
                "share": 150
            }
        )

        for item in self.priority_results:
            tree.insert(
                "",
                tk.END,
                values=(
                    item["rank"],
                    item["priority"],
                    item["file_count"],
                    self.storage_analyzer.format_size(
                        item["wasted_storage"]
                    ),
                    f"{item['waste_share']:.2f}%"
                )
            )

    # ---------------------------------------------------------
    # RAM USAGE VIEW
    # ---------------------------------------------------------

    def create_ram_view(self, parent):
        container = tk.Frame(parent, bg=self.bg)
        container.pack(fill="both", expand=True, padx=25, pady=25)

        tk.Label(
            container,
            text="Memory Usage Summary",
            bg=self.bg,
            fg=self.header,
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            container,
            text="System RAM measurements recorded during the scan.",
            bg=self.bg,
            fg="#64748B",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 20))

        data = [
            ("RAM Before Scan", self.ram_before, self.blue),
            ("Peak RAM Usage", self.ram_peak, self.purple),
            ("RAM After Scan", self.ram_after, self.green)
        ]

        for title, value, accent in data:
            card = tk.Frame(
                container,
                bg=self.white,
                highlightbackground="#E2E8F0",
                highlightthickness=1
            )
            card.pack(fill="x", pady=8)

            tk.Frame(
                card,
                bg=accent,
                width=6
            ).pack(side="left", fill="y")

            details = tk.Frame(card, bg=self.white)
            details.pack(
                side="left",
                fill="both",
                expand=True,
                padx=18,
                pady=16
            )

            tk.Label(
                details,
                text=title,
                bg=self.white,
                fg=self.dark,
                font=("Segoe UI", 11, "bold")
            ).pack(side="left")

            tk.Label(
                details,
                text=f"{value:.2f}%",
                bg=self.white,
                fg=accent,
                font=("Segoe UI", 17, "bold")
            ).pack(side="right")
        # ---------------------------------------------------------
    # DUPLICATES - PROFESSIONAL DESIGN
    # ---------------------------------------------------------

    def show_duplicates(self):
        if not self.duplicate_groups:
            messagebox.showinfo(
                "No Duplicates",
                "No duplicate groups were found.",
                parent=self.root
            )
            return

        window = tk.Toplevel(self.root)
        window.title("Duplicate Groups | Smart Deduplication")
        window.geometry("1100x700")
        window.minsize(900, 550)
        window.configure(bg=self.bg)
        self.add_back_button(window)
        # Header
        header = tk.Frame(
            window,
            bg=self.header,
            height=95
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Duplicate Groups",
            font=("Segoe UI", 20, "bold"),
            bg=self.header,
            fg=self.white
        ).pack(anchor="w", padx=25, pady=(15, 3))

        tk.Label(
            header,
            text="Review duplicate files and manage storage safely",
            font=("Segoe UI", 10),
            bg=self.header,
            fg="#CBD5E1"
        ).pack(anchor="w", padx=27)

        # Summary
        summary = tk.Frame(window, bg=self.bg)
        summary.pack(fill="x", padx=20, pady=15)

        total_groups = len(self.priority_results)
        total_duplicates = sum(
            item.get("file_count", 0)
            for item in self.priority_results
        )

        summary_items = [
            ("Duplicate Groups", total_groups, self.blue),
            ("Duplicate Files", total_duplicates, self.purple),
            (
                "Potential Saving",
                self.storage_analyzer.format_size(
                    self.potential_saving
                ),
                self.green
            )
        ]

        for title, value, accent in summary_items:
            card = tk.Frame(
                summary,
                bg=self.white,
                highlightbackground="#E2E8F0",
                highlightthickness=1
            )
            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=(0, 10)
            )

            tk.Frame(
                card,
                bg=accent,
                height=4
            ).pack(fill="x")

            tk.Label(
                card,
                text=title,
                bg=self.white,
                fg="#64748B",
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", padx=14, pady=(10, 2))

            tk.Label(
                card,
                text=str(value),
                bg=self.white,
                fg=self.dark,
                font=("Segoe UI", 16, "bold")
            ).pack(anchor="w", padx=14, pady=(0, 12))

        # Table area
        table_frame = tk.Frame(window, bg=self.white)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 12)
        )

        columns = (
            "group",
            "type",
            "files",
            "wasted",
            "priority"
        )

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "group": "Group",
            "type": "File Type",
            "files": "Files",
            "wasted": "Wasted Storage",
            "priority": "Priority"
        }

        widths = {
            "group": 130,
            "type": 250,
            "files": 100,
            "wasted": 200,
            "priority": 150
        }

        for column in columns:
            tree.heading(column, text=headings[column])
            tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        scrollbar_y = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree.yview
        )

        scrollbar_x = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=tree.xview
        )

        tree.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )

        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Populate duplicate groups
        for index, item in enumerate(
            self.priority_results,
            start=1
        ):
            extensions = []

            for file_info in item.get("files", []):
                extension = os.path.splitext(
                    file_info.get("name", "")
                )[1].lower()

                if not extension:
                    extension = "No Extension"

                if extension not in extensions:
                    extensions.append(extension)

            file_type = ", ".join(extensions) or "Unknown"

            tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    f"Group {index}",
                    file_type,
                    item.get("file_count", 0),
                    self.storage_analyzer.format_size(
                        item.get("wasted_storage", 0)
                    ),
                    item.get("priority", "Normal")
                )
            )

        # Action buttons
        button_frame = tk.Frame(
            window,
            bg=self.bg
        )
        button_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 18)
        )

        def make_button(text, color, command):
            button = tk.Button(
                button_frame,
                text=text,
                command=command,
                bg=color,
                fg=self.white,
                activebackground=self.header,
                activeforeground=self.white,
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Segoe UI", 10, "bold"),
                padx=17,
                pady=10
            )
            button.pack(side="left", padx=(0, 10))

            button.bind(
                "<Enter>",
                lambda event: button.config(
                    bg=self.header
                )
            )

            button.bind(
                "<Leave>",
                lambda event: button.config(
                    bg=color
                )
            )

            return button

        make_button(
            "View Files",
            self.blue,
            lambda: self.view_group_files(tree)
        )

        make_button(
            "Move",
            self.cyan,
            lambda: self.action_move(tree)
        )

        make_button(
            "Quarantine",
            self.orange,
            lambda: self.action_quarantine(tree)
        )

        make_button(
            "Recycle Bin",
            self.red,
            lambda: self.action_recycle(tree)
        )

        tk.Label(
            button_frame,
            text="Select a group before choosing an action.",
            bg=self.bg,
            fg="#64748B",
            font=("Segoe UI", 9)
        ).pack(side="right", padx=5)

    # ---------------------------------------------------------
    # GET SELECTED DUPLICATE GROUP
    # ---------------------------------------------------------

    def get_selected_group(self, tree):
        selection = tree.selection()

        if not selection:
            messagebox.showwarning(
                "Select Group",
                "Please select a duplicate group first.",
                parent=tree.winfo_toplevel()
            )
            return None

        index = int(selection[0]) - 1

        if index < 0 or index >= len(self.priority_results):
            return None

        return self.priority_results[index]

    # ---------------------------------------------------------
    # VIEW DUPLICATE FILE DETAILS
    # ---------------------------------------------------------

    def view_group_files(self, tree):
        item = self.get_selected_group(tree)

        if not item:
            return

        window = tk.Toplevel(self.root)
        window.title("Duplicate File Details")
        window.geometry("1250x680")
        window.minsize(950, 500)
        window.configure(bg=self.bg)
        self.add_back_button(window)
        # Header
        header = tk.Frame(
            window,
            bg=self.header,
            height=85
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Duplicate File Details",
            bg=self.header,
            fg=self.white,
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w", padx=22, pady=(12, 2))

        tk.Label(
            header,
            text="Review file names, sizes, locations and SHA-256 hashes",
            bg=self.header,
            fg="#CBD5E1",
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=24)

        # File table
        table_frame = tk.Frame(
            window,
            bg=self.white
        )
        table_frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        columns = (
            "number",
            "name",
            "type",
            "size",
            "location",
            "hash"
        )

        tree_view = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "number": "#",
            "name": "File Name",
            "type": "File Type",
            "size": "Size",
            "location": "Complete Path",
            "hash": "SHA-256 Hash"
        }

        widths = {
            "number": 55,
            "name": 190,
            "type": 110,
            "size": 110,
            "location": 450,
            "hash": 300
        }

        for column in columns:
            tree_view.heading(
                column,
                text=headings[column]
            )
            tree_view.column(
                column,
                width=widths[column],
                anchor="w"
            )

        scrollbar_y = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree_view.yview
        )

        scrollbar_x = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=tree_view.xview
        )

        tree_view.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )

        tree_view.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Populate file details
        files = item.get("files", [])

        for number, file_info in enumerate(files, start=1):
            file_path = file_info.get("path", "")

            file_name = file_info.get(
                "name",
                os.path.basename(file_path)
            )

            file_extension = os.path.splitext(file_name)[1].lower()

            if not file_extension:
                file_extension = "No Extension"

            file_size = self.storage_analyzer.format_size(
                file_info.get("size", 0)
            )

            file_hash = file_info.get(
                "hash",
                item.get("hash", "Not Available")
            )

            display_name = file_name

            if number == 1:
                display_name += "  [KEEP CANDIDATE]"

            tree_view.insert(
                "",
                tk.END,
                values=(
                    number,
                    display_name,
                    file_extension,
                    file_size,
                    file_path,
                    file_hash
                )
            )

        # Footer note
        footer = tk.Frame(
            window,
            bg=self.bg
        )
        footer.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(
            footer,
            text=(
                "Note: The first file is displayed as the Keep candidate. "
                "Verify the file before moving or removing any duplicate."
            ),
            bg=self.bg,
            fg="#475569",
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        # ---------------------------------------------------------
    # SAFE ACTIONS - IMPROVED DIALOGS
    # ---------------------------------------------------------

    def action_move(self, tree):
        item = self.get_selected_group(tree)

        if not item:
            return

        destination = filedialog.askdirectory(
            parent=tree.winfo_toplevel(),
            title="Select Destination Folder"
        )

        if not destination:
            return

        files = item["files"][1:]

        if not files:
            messagebox.showinfo(
                "Nothing to Move",
                "No duplicate copies are available to move.",
                parent=tree.winfo_toplevel()
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Move",
            f"Move {len(files)} duplicate file(s) to:\n\n"
            f"{destination}\n\n"
            "The first file in the group will be kept.\n"
            "Do you want to continue?",
            parent=tree.winfo_toplevel()
        )

        if not confirm:
            return

        try:
            moved = self.quarantine_manager.move_files(
                files,
                destination
            )

            messagebox.showinfo(
                "Move Complete",
                f"{len(moved)} duplicate file(s) moved successfully.",
                parent=tree.winfo_toplevel()
            )

        except Exception as error:
            messagebox.showerror(
                "Move Failed",
                f"Could not move the duplicate files.\n\n{error}",
                parent=tree.winfo_toplevel()
            )

    def action_quarantine(self, tree):
        item = self.get_selected_group(tree)

        if not item:
            return

        files = item["files"][1:]

        if not files:
            messagebox.showinfo(
                "Nothing to Quarantine",
                "No duplicate copies are available.",
                parent=tree.winfo_toplevel()
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Quarantine",
            f"Move {len(files)} duplicate file(s) "
            "to the quarantine folder?\n\n"
            "The first file in the group will be kept.\n"
            "Continue only if you have verified the selected group.",
            parent=tree.winfo_toplevel()
        )

        if not confirm:
            return

        try:
            moved = self.quarantine_manager.quarantine_files(
                files,
                item["rank"]
            )

            messagebox.showinfo(
                "Quarantine Complete",
                f"{len(moved)} file(s) moved to quarantine.",
                parent=tree.winfo_toplevel()
            )

        except Exception as error:
            messagebox.showerror(
                "Quarantine Failed",
                f"Could not quarantine the files.\n\n{error}",
                parent=tree.winfo_toplevel()
            )

    def action_recycle(self, tree):
        item = self.get_selected_group(tree)

        if not item:
            return

        files = item["files"][1:]

        if not files:
            messagebox.showinfo(
                "Nothing to Recycle",
                "No duplicate copies are available.",
                parent=tree.winfo_toplevel()
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Recycle",
            f"Send {len(files)} duplicate file(s) "
            "to the Windows Recycle Bin?\n\n"
            "The first file in the group will be kept.\n"
            "Please verify the files before continuing.",
            parent=tree.winfo_toplevel()
        )

        if not confirm:
            return

        try:
            recycled = self.quarantine_manager.recycle_files(
                files
            )

            messagebox.showinfo(
                "Recycle Complete",
                f"{len(recycled)} file(s) sent to the Recycle Bin.",
                parent=tree.winfo_toplevel()
            )

        except Exception as error:
            messagebox.showerror(
                "Recycle Failed",
                f"Could not recycle the files.\n\n{error}",
                parent=tree.winfo_toplevel()
            )
        # ---------------------------------------------------------
    # PROFESSIONAL STORAGE ANALYTICS DASHBOARD
    # ---------------------------------------------------------

    def show_graphs(self):

        if not self.files:
            messagebox.showinfo(
                "No Scan Available",
                "Please scan a folder first.",
                parent=self.root
            )
            return

        self.show_storage_graph()

    def show_storage_graph(self):

        # Calculate storage statistics
        total_size = sum(
            max(0, file.get("size", 0))
            for file in self.files
        )

        potential_saving = min(
            total_size,
            max(0, getattr(self, "potential_saving", 0))
        )

        optimized_size = max(0, total_size - potential_saving)
        total_files = len(self.files)

        duplicate_files = sum(
            max(0, len(group.get("files", [])) - 1)
            for group in getattr(self, "priority_results", [])
        )

        duplicate_files = min(duplicate_files, total_files)

        # Create dashboard window
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Storage Analytics Dashboard")
        graph_window.geometry("1100x760")
        graph_window.minsize(850, 600)
        graph_window.configure(bg="#F1F5F9")
        self.add_back_button(graph_window)
        # Header
        header = tk.Frame(
            graph_window,
            bg="#172554",
            height=85
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Storage Analytics Dashboard",
            font=("Segoe UI", 21, "bold"),
            bg="#172554",
            fg="#FFFFFF"
        ).pack(anchor="w", padx=25, pady=(15, 2))

        tk.Label(
            header,
            text="Visual insights into storage usage and optimization",
            font=("Segoe UI", 10),
            bg="#172554",
            fg="#CBD5E1"
        ).pack(anchor="w", padx=27)

        # Summary cards
        cards_frame = tk.Frame(
            graph_window,
            bg="#F1F5F9"
        )
        cards_frame.pack(fill="x", padx=18, pady=18)

        def format_size(size):
            size = float(max(0, size))
            units = ["B", "KB", "MB", "GB", "TB"]

            for unit in units:
                if size < 1024 or unit == "TB":
                    return f"{size:.2f} {unit}"
                size /= 1024

        savings_percent = (
            potential_saving / total_size * 100
            if total_size > 0 else 0
        )

        card_data = [
            ("TOTAL STORAGE", format_size(total_size), "#2563EB"),
            ("POTENTIAL SAVING", format_size(potential_saving), "#059669"),
            ("DUPLICATE FILES", str(duplicate_files), "#D97706"),
            ("SPACE SAVABLE", f"{savings_percent:.1f}%", "#7C3AED")
        ]

        for index, (title, value, accent) in enumerate(card_data):

            card = tk.Frame(
                cards_frame,
                bg="#FFFFFF",
                highlightbackground="#E2E8F0",
                highlightthickness=1
            )
            card.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=6,
                pady=4
            )

            cards_frame.grid_columnconfigure(index, weight=1)

            tk.Frame(
                card,
                bg=accent,
                height=4
            ).pack(fill="x")

            tk.Label(
                card,
                text=title,
                font=("Segoe UI", 9, "bold"),
                bg="#FFFFFF",
                fg="#64748B"
            ).pack(anchor="w", padx=12, pady=(12, 5))

            tk.Label(
                card,
                text=value,
                font=("Segoe UI", 16, "bold"),
                bg="#FFFFFF",
                fg=accent
            ).pack(anchor="w", padx=12, pady=(0, 14))

        # Charts area
        charts_frame = tk.Frame(
            graph_window,
            bg="#F1F5F9"
        )
        charts_frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 10)
        )

        # Create two charts in one figure
        figure = Figure(
            figsize=(10, 5.2),
            dpi=100,
            facecolor="#F1F5F9"
        )

        # Chart 1: Storage distribution
        ax1 = figure.add_subplot(121)

        if total_size > 0:

            if potential_saving > 0:
                ax1.pie(
                    [optimized_size, potential_saving],
                    labels=[
                        "Storage After\nOptimization",
                        "Potential Saving"
                    ],
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=["#2563EB", "#10B981"],
                    wedgeprops={
                        "width": 0.38,
                        "edgecolor": "#FFFFFF",
                        "linewidth": 2
                    },
                    textprops={"fontsize": 9}
                )

                ax1.text(
                    0, 0,
                    f"{savings_percent:.1f}%\nSavable",
                    ha="center",
                    va="center",
                    fontsize=13,
                    fontweight="bold",
                    color="#0F172A"
                )

            else:
                ax1.pie(
                    [total_size],
                    labels=["Used Storage"],
                    colors=["#2563EB"],
                    startangle=90,
                    wedgeprops={
                        "width": 0.38,
                        "edgecolor": "#FFFFFF",
                        "linewidth": 2
                    }
                )

                ax1.text(
                    0, 0,
                    "0%\nSavable",
                    ha="center",
                    va="center",
                    fontsize=13,
                    fontweight="bold",
                    color="#0F172A"
                )

        else:
            ax1.text(
                0.5, 0.5,
                "No storage data available",
                ha="center",
                va="center",
                transform=ax1.transAxes
            )

        ax1.set_title(
            "Storage Distribution",
            fontsize=13,
            fontweight="bold",
            color="#0F172A",
            pad=18
        )

        # Chart 2: Before and after comparison
        ax2 = figure.add_subplot(122)

        bars = ax2.bar(
            ["Before\nOptimization", "After\nOptimization"],
            [total_size, optimized_size],
            color=["#60A5FA", "#059669"],
            width=0.55
        )

        ax2.set_title(
            "Storage Comparison",
            fontsize=13,
            fontweight="bold",
            color="#0F172A",
            pad=18
        )

        ax2.set_ylabel(
            "Storage Size (Bytes)",
            fontsize=9
        )

        ax2.set_ylim(
            0,
            max(total_size * 1.20, 1)
        )

        ax2.grid(
            axis="y",
            linestyle="--",
            alpha=0.25
        )

        ax2.set_axisbelow(True)

        for bar, value in zip(
            bars,
            [total_size, optimized_size]
        ):
            ax2.annotate(
                format_size(value),
                (
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height()
                ),
                xytext=(0, 6),
                textcoords="offset points",
                ha="center",
                fontsize=9,
                fontweight="bold"
            )

        figure.tight_layout(pad=3)

        # Display charts inside the Tkinter window
        canvas = FigureCanvasTkAgg(
            figure,
            master=charts_frame
        )
        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        # Footer
        footer = tk.Frame(
            graph_window,
            bg="#FFFFFF"
        )
        footer.pack(fill="x", side="bottom")

        tk.Label(
            footer,
            text=(
                f"Files scanned: {total_files}    |    "
                f"Potential storage saving: {format_size(potential_saving)}"
            ),
            font=("Segoe UI", 10),
            bg="#FFFFFF",
            fg="#475569",
            pady=12
        ).pack(side="left", padx=20)

        tk.Button(
            footer,
            text="Close Dashboard",
            command=graph_window.destroy,
            font=("Segoe UI", 10, "bold"),
            bg="#172554",
            fg="#FFFFFF",
            activebackground="#1E40AF",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=7
        ).pack(side="right", padx=20, pady=8)
        # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def set_status(self, text, color):
        self.status_label.config(
            text=text,
            fg=color
        )

    def set_info(self, text):
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert(tk.END, text)
        self.info_text.config(state="disabled")
        # ---------------------------------------------------------
    # SCAN HISTORY
    # ---------------------------------------------------------

    def show_history(self):
        """Display saved scan history from the SQLite database."""

        window = tk.Toplevel(self.root)
        window.title("Scan History | Smart Data Deduplication")
        window.geometry("1180x520")
        window.minsize(900, 400)
        window.configure(bg="#F1F5F9")
        self.add_back_button(window)      
        tk.Label(
            window,
            text="Scan History",
            font=("Segoe UI", 20, "bold"),
            bg="#F1F5F9",
            fg="#172554"
        ).pack(anchor="w", padx=20, pady=(16, 3))

        tk.Label(
            window,
            text="Previously completed scans saved in the local database.",
            font=("Segoe UI", 10),
            bg="#F1F5F9",
            fg="#64748B"
        ).pack(anchor="w", padx=20, pady=(0, 12))

        table_frame = tk.Frame(window, bg="#FFFFFF")
        table_frame.pack(fill="both", expand=True, padx=18, pady=(0, 12))

        columns = (
            "date", "folder", "files", "size", "groups", "duplicates",
            "wasted", "saving", "percent", "skipped", "time"
        )
        tree = ttk.Treeview(
            table_frame, columns=columns, show="headings"
        )

        headings = {
            "date": "Scan Date",
            "folder": "Folder",
            "files": "Total Files",
            "size": "Total Size (bytes)",
            "groups": "Duplicate Groups",
            "duplicates": "Duplicate Files",
            "wasted": "Storage Wasted (bytes)",
            "saving": "Potential Saving (bytes)",
            "percent": "Saving %",
            "skipped": "Skipped",
            "time": "Scan Time (s)"
        }
        for column, heading in headings.items():
            tree.heading(column, text=heading)
            tree.column(column, width=115, minwidth=90, anchor="w")

        tree.column("date", width=145)
        tree.column("folder", width=260)
        tree.column("files", width=85, anchor="center")
        tree.column("groups", width=110, anchor="center")
        tree.column("duplicates", width=110, anchor="center")
        tree.column("percent", width=80, anchor="center")
        tree.column("skipped", width=75, anchor="center")
        tree.column("time", width=95, anchor="center")

        y_scroll = ttk.Scrollbar(
            table_frame, orient="vertical", command=tree.yview
        )
        x_scroll = ttk.Scrollbar(
            table_frame, orient="horizontal", command=tree.xview
        )
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        def refresh_history():
            for item in tree.get_children():
                tree.delete(item)
            try:
                records = self.database.get_scan_history()
            except Exception as error:
                messagebox.showerror(
                    "History Error",
                    f"Could not load scan history.\n\n{error}",
                    parent=window
                )
                return

            for row in records:
                values = list(row)
                # Saving percentage and scan duration are easier to read this way.
                values[8] = f"{float(values[8] or 0):.2f}%"
                values[10] = f"{float(values[10] or 0):.2f}"
                tree.insert("", tk.END, values=values)

            status.config(
                text=f"{len(records)} scan record(s) found."
            )

        status = tk.Label(
            window, text="Loading history...",
            bg="#E2E8F0", fg="#334155",
            anchor="w", padx=12, pady=7
        )
        status.pack(fill="x", padx=18, pady=(0, 8))

        buttons = tk.Frame(window, bg="#F1F5F9")
        buttons.pack(fill="x", padx=18, pady=(0, 14))

        tk.Button(
            buttons, text="Refresh", command=refresh_history,
            bg="#2563EB", fg="white", relief="flat",
            font=("Segoe UI", 10, "bold"), padx=16, pady=7,
            cursor="hand2"
        ).pack(side="left")

        def clear_history():
            if not messagebox.askyesno(
                "Clear Scan History",
                "Delete all saved scan-history records? This does not delete scanned files.",
                parent=window
            ):
                return
            try:
                self.database.clear_history()
                refresh_history()
            except Exception as error:
                messagebox.showerror(
                    "History Error", str(error), parent=window
                )

        tk.Button(
            buttons, text="Clear History", command=clear_history,
            bg="#DC2626", fg="white", relief="flat",
            font=("Segoe UI", 10, "bold"), padx=16, pady=7,
            cursor="hand2"
        ).pack(side="left", padx=8)

        refresh_history()

    def generate_reports(self):
        """Generate CSV and PDF reports for the latest completed scan."""

        if not self.files:
            messagebox.showwarning(
                "No Scan Results",
                "Please select a folder and complete a scan before generating reports.",
                parent=self.root
            )
            return

        try:
            common_args = (
                self.selected_folder,
                self.files,
                self.duplicate_groups,
                self.storage_wasted,
                self.potential_saving,
                self.saving_percentage
            )

            csv_path = self.report_generator.generate_csv_report(
                *common_args,
                folder_analysis=self.folder_analysis,
                extension_analysis=self.extension_analysis,
                priority_results=self.priority_results
            )

            pdf_path = self.report_generator.generate_pdf_report(
                *common_args,
                folder_analysis=self.folder_analysis,
                extension_analysis=self.extension_analysis,
                priority_results=self.priority_results,
                ram_before=self.ram_before,
                ram_peak=self.ram_peak,
                ram_after=self.ram_after,
                scan_time=self.scan_time
            )

            messagebox.showinfo(
                "Reports Generated",
                "Both reports were generated successfully.\n\n"
                f"CSV Report:\n{csv_path}\n\nPDF Report:\n{pdf_path}",
                parent=self.root
            )

        except Exception as error:
            messagebox.showerror(
                "Report Generation Failed",
                f"Could not generate reports.\n\n{error}",
                parent=self.root
            )

    def open_report_manager(self):
        """List generated CSV/PDF reports and open the selected report."""

        report_folder = self.report_generator.report_folder
        os.makedirs(report_folder, exist_ok=True)

        window = tk.Toplevel(self.root)
        window.title("Report Manager | Smart Data Deduplication")
        window.geometry("850x500")
        window.minsize(650, 350)
        window.configure(bg="#F1F5F9")
        self.add_back_button(window)
        tk.Label(
            window, text="Generated Reports",
            font=("Segoe UI", 20, "bold"),
            bg="#F1F5F9", fg="#172554"
        ).pack(anchor="w", padx=20, pady=(16, 3))

        tk.Label(
            window, text=f"Report folder: {os.path.abspath(report_folder)}",
            font=("Segoe UI", 9), bg="#F1F5F9", fg="#64748B"
        ).pack(anchor="w", padx=20, pady=(0, 12))

        table_frame = tk.Frame(window, bg="#FFFFFF")
        table_frame.pack(fill="both", expand=True, padx=18, pady=(0, 10))

        tree = ttk.Treeview(
            table_frame, columns=("name", "type", "modified", "path"),
            show="headings", selectmode="browse"
        )
        for column, title, width in [
            ("name", "Report Name", 260),
            ("type", "Type", 75),
            ("modified", "Last Modified", 145),
            ("path", "File Path", 330)
        ]:
            tree.heading(column, text=title)
            tree.column(column, width=width, minwidth=90, anchor="w")

        y_scroll = ttk.Scrollbar(
            table_frame, orient="vertical", command=tree.yview
        )
        x_scroll = ttk.Scrollbar(
            table_frame, orient="horizontal", command=tree.xview
        )
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        status = tk.StringVar(value="Ready")
        tk.Label(
            window, textvariable=status,
            bg="#E2E8F0", fg="#334155", anchor="w",
            padx=12, pady=7
        ).pack(fill="x", padx=18, pady=(0, 8))

        def refresh_reports():
            for item in tree.get_children():
                tree.delete(item)
            report_files = []
            for name in os.listdir(report_folder):
                full_path = os.path.abspath(os.path.join(report_folder, name))
                if os.path.isfile(full_path) and os.path.splitext(name)[1].lower() in (".csv", ".pdf"):
                    report_files.append(full_path)
            report_files.sort(key=os.path.getmtime, reverse=True)

            for full_path in report_files:
                modified = datetime.fromtimestamp(
                    os.path.getmtime(full_path)
                ).strftime("%Y-%m-%d %H:%M")
                tree.insert(
                    "", tk.END, values=(
                        os.path.basename(full_path),
                        os.path.splitext(full_path)[1][1:].upper(),
                        modified,
                        full_path
                    )
                )
            status.set(f"{len(report_files)} report(s) found.")

        def open_selected():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning(
                    "Select a Report", "Please select a report first.",
                    parent=window
                )
                return
            selected_path = tree.item(selection[0], "values")[3]
            if not os.path.exists(selected_path):
                messagebox.showerror(
                    "File Not Found", "This report file no longer exists.",
                    parent=window
                )
                refresh_reports()
                return
            try:
                os.startfile(selected_path)
            except Exception as error:
                messagebox.showerror(
                    "Unable to Open Report",
                    f"Could not open the report.\n\n{error}",
                    parent=window
                )

        buttons = tk.Frame(window, bg="#F1F5F9")
        buttons.pack(fill="x", padx=18, pady=(0, 14))
        tk.Button(
            buttons, text="Open Selected", command=open_selected,
            bg="#0284C7", fg="white", relief="flat",
            font=("Segoe UI", 10, "bold"), padx=16, pady=7,
            cursor="hand2"
        ).pack(side="left")
        tk.Button(
            buttons, text="Refresh", command=refresh_reports,
            bg="#2563EB", fg="white", relief="flat",
            font=("Segoe UI", 10, "bold"), padx=16, pady=7,
            cursor="hand2"
        ).pack(side="left", padx=8)
        tk.Button(
            buttons, text="Open Reports Folder",
            command=lambda: os.startfile(os.path.abspath(report_folder)),
            bg="#7C3AED", fg="white", relief="flat",
            font=("Segoe UI", 10, "bold"), padx=16, pady=7,
            cursor="hand2"
        ).pack(side="left")

        tree.bind("<Double-1>", lambda _event: open_selected())
        refresh_reports()

    # ---------------------------------------------------------
    # PROFESSIONAL QUARANTINE MANAGER
    # ---------------------------------------------------------

    def open_quarantine_manager(self):
        """Manage, restore, and remove quarantined files safely."""

        window = tk.Toplevel(self.root)
        window.title("Quarantine Manager | Storage Optimization")
        window.geometry("1150x650")
        window.minsize(850, 500)
        window.configure(bg="#F1F5F9")
        self.add_back_button(window)
        # Header
        header = tk.Frame(
            window,
            bg="#172554",
            height=95
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Quarantine Manager",
            font=("Segoe UI", 22, "bold"),
            bg="#172554",
            fg="#FFFFFF"
        ).pack(anchor="w", padx=24, pady=(14, 3))

        tk.Label(
            header,
            text="Review quarantined files, restore them, or manage stored copies.",
            font=("Segoe UI", 10),
            bg="#172554",
            fg="#CBD5E1"
        ).pack(anchor="w", padx=26)

        # Summary panel
        summary = tk.Frame(
            window,
            bg="#FFFFFF",
            highlightbackground="#E2E8F0",
            highlightthickness=1
        )
        summary.pack(fill="x", padx=18, pady=(16, 10))

        tk.Label(
            summary,
            text="QUARANTINE STORAGE",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#64748B"
        ).pack(anchor="w", padx=16, pady=(10, 2))

        count_label = tk.Label(
            summary,
            text="Loading quarantined files...",
            font=("Segoe UI", 13, "bold"),
            bg="#FFFFFF",
            fg="#2563EB"
        )
        count_label.pack(anchor="w", padx=16, pady=(0, 10))

        # Table container
        table_frame = tk.Frame(
            window,
            bg="#FFFFFF"
        )
        table_frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 10)
        )

        columns = (
            "name",
            "size",
            "quarantined",
            "original",
            "stored"
        )

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = [
            ("name", "File Name"),
            ("size", "File Size"),
            ("quarantined", "Quarantine Date"),
            ("original", "Original Location"),
            ("stored", "Quarantine Location")
        ]

        for col, heading in headings:
            tree.heading(col, text=heading)

        tree.column("name", width=180, minwidth=130)
        tree.column("size", width=100, minwidth=80, anchor="e")
        tree.column("quarantined", width=150, minwidth=120)
        tree.column("original", width=300, minwidth=180)
        tree.column("stored", width=350, minwidth=200)

        ybar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree.yview
        )

        xbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=tree.xview
        )

        tree.configure(
            yscrollcommand=ybar.set,
            xscrollcommand=xbar.set
        )

        tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        tree.tag_configure(
            "even",
            background="#F8FAFC"
        )
        tree.tag_configure(
            "odd",
            background="#FFFFFF"
        )

        # Status bar
        status = tk.StringVar(value="Ready")

        tk.Label(
            window,
            textvariable=status,
            bg="#E2E8F0",
            fg="#334155",
            anchor="w",
            font=("Segoe UI", 9),
            padx=12,
            pady=7
        ).pack(fill="x", padx=18, pady=(0, 8))

        # Refresh table
        def refresh():
            for row in tree.get_children():
                tree.delete(row)

            try:
                items = self.quarantine_manager.list_quarantined_files()
            except (OSError, ValueError) as error:
                messagebox.showerror(
                    "Quarantine Error",
                    str(error),
                    parent=window
                )
                status.set("Unable to load quarantine files.")
                return

            total_size = 0

            for index, item in enumerate(items):
                path = item["path"]

                try:
                    file_size = os.path.getsize(path)
                    size = self.storage_analyzer.format_size(file_size)
                    total_size += file_size
                except OSError:
                    size = "Unknown"

                original = (
                    item.get("source")
                    or "Not recorded — choose a restore folder"
                )

                tree.insert(
                    "",
                    tk.END,
                    iid=str(index),
                    values=(
                        os.path.basename(path),
                        size,
                        item.get("quarantined", "Unknown"),
                        original,
                        path
                    ),
                    tags=("even" if index % 2 == 0 else "odd",)
                )

            count_label.config(
                text=(
                    f"{len(items)} quarantined file(s)  |  "
                    f"Total size: "
                    f"{self.storage_analyzer.format_size(total_size)}"
                )
            )

            status.set(
                f"{len(items)} quarantined file(s) loaded successfully."
            )

        # Get selected file
        def selected_item():
            selection = tree.selection()

            if not selection:
                messagebox.showwarning(
                    "Select a File",
                    "Please select a quarantined file first.",
                    parent=window
                )
                return None

            values = tree.item(selection[0], "values")

            return {
                "path": values[4],
                "source": values[3]
            }

        # Restore selected file
        def restore_selected():
            item = selected_item()

            if not item:
                return

            fallback_folder = None

            if (
                not item["source"]
                or item["source"].startswith("Not recorded")
            ):
                fallback_folder = filedialog.askdirectory(
                    parent=window,
                    title="Choose Folder to Restore File"
                )

                if not fallback_folder:
                    return

            if not messagebox.askyesno(
                "Confirm Restore",
                "Restore the selected file from quarantine?",
                parent=window
            ):
                return

            try:
                restored_path = self.quarantine_manager.restore_file(
                    item["path"],
                    fallback_folder=fallback_folder
                )

                if restored_path:
                    status.set(f"Restored: {restored_path}")

                    messagebox.showinfo(
                        "Restore Complete",
                        f"File restored successfully:\n\n{restored_path}",
                        parent=window
                    )

                    refresh()

                else:
                    messagebox.showerror(
                        "Restore Failed",
                        "The file could not be restored. "
                        "Check permissions and available disk space.",
                        parent=window
                    )

            except (OSError, ValueError) as error:
                messagebox.showerror(
                    "Restore Error",
                    str(error),
                    parent=window
                )

        # Permanently delete selected file
        def delete_selected():
            item = selected_item()

            if not item:
                return

            confirm = messagebox.askyesno(
                "Permanent Deletion Warning",
                "This action permanently deletes the selected quarantined file.\n\n"
                "The file will NOT go to the Recycle Bin and may not be recoverable.\n\n"
                "Are you sure you want to continue?",
                icon="warning",
                parent=window
            )

            if not confirm:
                return

            try:
                self.quarantine_manager.delete_quarantined_file(
                    item["path"]
                )

                status.set("Selected file permanently deleted.")

                messagebox.showinfo(
                    "Deletion Complete",
                    "The selected quarantined file was deleted.",
                    parent=window
                )

                refresh()

            except (OSError, ValueError) as error:
                messagebox.showerror(
                    "Delete Error",
                    str(error),
                    parent=window
                )

        # Open quarantine folder
        def open_folder():
            folder = self.quarantine_manager.quarantine_root

            try:
                os.makedirs(folder, exist_ok=True)

                if os.name == "nt":
                    os.startfile(os.path.abspath(folder))
                else:
                    import webbrowser
                    webbrowser.open(
                        "file://" + os.path.abspath(folder)
                    )

            except OSError as error:
                messagebox.showerror(
                    "Open Folder Error",
                    str(error),
                    parent=window
                )

        # Buttons
        buttons = tk.Frame(
            window,
            bg="#F1F5F9"
        )
        buttons.pack(fill="x", padx=18, pady=(0, 15))

        def make_button(parent, text, command, color):
            button = tk.Button(
                parent,
                text=text,
                command=command,
                font=("Segoe UI", 9, "bold"),
                bg=color,
                fg="#FFFFFF",
                activebackground=color,
                activeforeground="#FFFFFF",
                relief="flat",
                cursor="hand2",
                padx=14,
                pady=9
            )

            button.pack(side="left", padx=(0, 9))

            return button

        make_button(
            buttons,
            "Restore Selected",
            restore_selected,
            "#059669"
        )

        make_button(
            buttons,
            "Delete Permanently",
            delete_selected,
            "#DC2626"
        )

        make_button(
            buttons,
            "Refresh",
            refresh,
            "#2563EB"
        )

        make_button(
            buttons,
            "Open Quarantine Folder",
            open_folder,
            "#7C3AED"
        )

        refresh()


# -------------------------------------------------------------
# APPLICATION START
# -------------------------------------------------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = SmartDeduplicationApp(root)

    root.mainloop()
    