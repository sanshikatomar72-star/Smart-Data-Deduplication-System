import os


class FileScanner:
    """
    Recursive file scanner with optional live progress updates and cancellation.

    Backward compatibility:
        scanner.scan_folder(folder_path)

    Live progress:
        scanner.scan_folder(folder_path, progress_callback=callback)

    Cancellation:
        scanner.scan_folder(folder_path, stop_event=threading.Event())
        Call stop_event.set() from the GUI Stop Scanning button.

    progress_callback receives a dictionary containing:
        processed, total_found, files_found, skipped, current_file,
        current_path, stopped
    """

    def __init__(self):
        self.files = []
        self.skipped_files = []
        self.total_found = 0
        self.processed_files = 0
        self.is_stopped = False

    def scan_folder(self, folder_path, progress_callback=None, stop_event=None):
        self.files = []
        self.skipped_files = []
        self.total_found = 0
        self.processed_files = 0
        self.is_stopped = False

        folder_path = os.path.abspath(folder_path)

        def report_progress(current_file="", current_path=""):
            if callable(progress_callback):
                progress_callback({
                    "processed": self.processed_files,
                    "total_found": self.total_found,
                    "files_found": len(self.files),
                    "skipped": len(self.skipped_files),
                    "current_file": current_file,
                    "current_path": current_path,
                    "stopped": self.is_stopped,
                })

        for root, directories, filenames in os.walk(folder_path):
            # Check cancellation between directories and files.
            if stop_event is not None and stop_event.is_set():
                self.is_stopped = True
                break

            for filename in filenames:
                if stop_event is not None and stop_event.is_set():
                    self.is_stopped = True
                    break

                file_path = os.path.join(root, filename)
                self.total_found += 1
                self.processed_files += 1
                try:
                    if not os.path.isfile(file_path):
                        report_progress(filename, file_path)
                        continue

                    file_size = os.path.getsize(file_path)

                    relative_path = os.path.relpath(
                        file_path,
                        folder_path
                    )

                    relative_folder = os.path.dirname(relative_path)

                    if relative_folder == "":
                        relative_folder = "Selected Folder"

                    extension = os.path.splitext(filename)[1].lower()

                    if extension == "":
                        extension = "No Extension"

                    file_info = {
                        "name": filename,
                        "path": file_path,
                        "size": file_size,
                        "extension": extension,
                        "folder": relative_folder
                    }

                    self.files.append(file_info)

                except (PermissionError, OSError) as error:
                    self.skipped_files.append({
                        "name": filename,
                        "path": file_path,
                        "error": str(error)
                    })

                finally:
                    report_progress(filename, file_path)

            if self.is_stopped:
                break

        report_progress()
        return self.files

    def get_total_files(self):
        return len(self.files)

    def get_total_size(self):
        total_size = 0
        for file in self.files:
            total_size += file["size"]
        return total_size

    def get_total_found(self):
        return self.total_found

    def get_processed_files(self):
        return self.processed_files

    def get_is_stopped(self):
        return self.is_stopped

    def get_skipped_count(self):
        return len(self.skipped_files)

    def get_skipped_files(self):
        return self.skipped_files

    def get_folder_analysis(self):
        folder_data = {}

        for file in self.files:
            folder = file["folder"]

            if folder not in folder_data:
                folder_data[folder] = {
                    "files": 0,
                    "size": 0
                }

            folder_data[folder]["files"] += 1
            folder_data[folder]["size"] += file["size"]

        return folder_data

    def get_extension_analysis(self):
        extension_data = {}

        for file in self.files:
            extension = file["extension"]

            if extension not in extension_data:
                extension_data[extension] = {
                    "files": 0,
                    "size": 0
                }

            extension_data[extension]["files"] += 1
            extension_data[extension]["size"] += file["size"]

        return extension_data

