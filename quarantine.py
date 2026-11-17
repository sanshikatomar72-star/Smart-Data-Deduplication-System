import os
import json
import shutil
import ctypes
from datetime import datetime


class QuarantineManager:
    """Moves duplicate candidates to quarantine and keeps restore metadata."""

    MANIFEST_NAME = "quarantine_manifest.json"

    def __init__(self, quarantine_root="quarantine"):
        self.quarantine_root = os.path.abspath(quarantine_root)
        os.makedirs(self.quarantine_root, exist_ok=True)

    def _manifest_path(self, folder):
        return os.path.join(folder, self.MANIFEST_NAME)

    def _read_manifest(self, folder):
        path = self._manifest_path(folder)
        if not os.path.isfile(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def _write_manifest(self, folder, records):
        os.makedirs(folder, exist_ok=True)
        path = self._manifest_path(folder)
        temp_path = path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(records, file, indent=2, ensure_ascii=False)
        os.replace(temp_path, path)

    def quarantine_files(self, files, group_number):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        group_folder = os.path.join(
            self.quarantine_root,
            f"scan_{timestamp}",
            f"Group_{group_number}"
        )
        os.makedirs(group_folder, exist_ok=True)
        moved = []
        records = self._read_manifest(group_folder)

        for file_info in files:
            source = os.path.abspath(file_info.get("path", ""))
            if not os.path.isfile(source):
                continue

            destination = self._unique_destination(
                os.path.join(group_folder, os.path.basename(source))
            )
            try:
                shutil.move(source, destination)
                record = {
                    "source": source,
                    "destination": os.path.abspath(destination),
                    "quarantined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                records.append(record)
                self._write_manifest(group_folder, records)
                moved.append({
                    "source": source,
                    "destination": destination
                })
            except (PermissionError, OSError):
                continue
        return moved

    def list_quarantined_files(self):
        """Return quarantined files and any saved original-path metadata."""
        items = []
        if not os.path.isdir(self.quarantine_root):
            return items

        for current_root, _dirs, filenames in os.walk(self.quarantine_root):
            records = self._read_manifest(current_root)
            records_by_destination = {
                os.path.normcase(os.path.abspath(r.get("destination", ""))): r
                for r in records if r.get("destination")
            }
            for filename in filenames:
                if filename == self.MANIFEST_NAME or filename.endswith(".tmp"):
                    continue
                path = os.path.abspath(os.path.join(current_root, filename))
                if not os.path.isfile(path):
                    continue
                record = records_by_destination.get(os.path.normcase(path), {})
                try:
                    quarantined = record.get(
                        "quarantined",
                        datetime.fromtimestamp(os.path.getmtime(path)).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    )
                except OSError:
                    quarantined = "Unknown"
                items.append({
                    "path": path,
                    "source": record.get("source", ""),
                    "quarantined": quarantined
                })
        items.sort(key=lambda item: item.get("quarantined", ""), reverse=True)
        return items

    def _find_record(self, destination):
        destination = os.path.normcase(os.path.abspath(destination))
        for current_root, _dirs, _files in os.walk(self.quarantine_root):
            records = self._read_manifest(current_root)
            for record in records:
                saved = record.get("destination", "")
                if saved and os.path.normcase(os.path.abspath(saved)) == destination:
                    return current_root, records, record
        return None, [], None

    def restore_file(self, quarantined_path, fallback_folder=None):
        """Restore one file; never overwrite an existing file."""
        quarantined_path = os.path.abspath(quarantined_path)
        if not os.path.isfile(quarantined_path):
            raise FileNotFoundError("The quarantined file no longer exists.")

        manifest_folder, records, record = self._find_record(quarantined_path)
        original = record.get("source") if record else None

        if original:
            target_folder = os.path.dirname(original)
            target = original
        elif fallback_folder:
            target_folder = os.path.abspath(fallback_folder)
            target = os.path.join(target_folder, os.path.basename(quarantined_path))
        else:
            raise ValueError(
                "Original location is not recorded. Choose a destination folder to restore."
            )

        os.makedirs(target_folder, exist_ok=True)
        target = self._unique_destination(target)

        shutil.move(quarantined_path, target)

        if record and manifest_folder:
            remaining = [
                r for r in records
                if os.path.normcase(os.path.abspath(r.get("destination", "")))
                != os.path.normcase(quarantined_path)
            ]
            self._write_manifest(manifest_folder, remaining)
            self._remove_empty_quarantine_folders(manifest_folder)
        return target

    def delete_quarantined_file(self, quarantined_path):
        """Permanently delete a selected quarantined file and update its manifest."""
        quarantined_path = os.path.abspath(quarantined_path)
        if not os.path.isfile(quarantined_path):
            raise FileNotFoundError("The quarantined file no longer exists.")

        manifest_folder, records, record = self._find_record(quarantined_path)
        os.remove(quarantined_path)

        if record and manifest_folder:
            remaining = [
                r for r in records
                if os.path.normcase(os.path.abspath(r.get("destination", "")))
                != os.path.normcase(quarantined_path)
            ]
            self._write_manifest(manifest_folder, remaining)
            self._remove_empty_quarantine_folders(manifest_folder)

    def _remove_empty_quarantine_folders(self, folder):
        current = os.path.abspath(folder)
        root = os.path.abspath(self.quarantine_root)
        while current != root and current.startswith(root + os.sep):
            try:
                if os.listdir(current):
                    break
                os.rmdir(current)
            except OSError:
                break
            current = os.path.dirname(current)

    def move_files(self, files, destination_folder):
        os.makedirs(destination_folder, exist_ok=True)
        moved = []
        for file_info in files:
            source = file_info.get("path", "")
            if not os.path.isfile(source):
                continue
            destination = self._unique_destination(
                os.path.join(destination_folder, os.path.basename(source))
            )
            try:
                shutil.move(source, destination)
                moved.append({"source": source, "destination": destination})
            except (PermissionError, OSError):
                continue
        return moved

    def recycle_files(self, files):
        if os.name != "nt":
            raise OSError("Recycle Bin action is supported on Windows only.")
        recycled = []
        for file_info in files:
            source = file_info.get("path", "")
            if not os.path.isfile(source):
                continue
            try:
                if self._send_to_recycle_bin(source):
                    recycled.append(source)
            except (PermissionError, OSError):
                continue
        return recycled

    @staticmethod
    def _unique_destination(destination):
        if not os.path.exists(destination):
            return destination
        base, extension = os.path.splitext(destination)
        counter = 1
        while True:
            new_destination = f"{base}_copy{counter}{extension}"
            if not os.path.exists(new_destination):
                return new_destination
            counter += 1

    @staticmethod
    def _send_to_recycle_bin(path):
        class SHFILEOPSTRUCTW(ctypes.Structure):
            _fields_ = [
                ("hwnd", ctypes.c_void_p),
                ("wFunc", ctypes.c_uint),
                ("pFrom", ctypes.c_wchar_p),
                ("pTo", ctypes.c_wchar_p),
                ("fFlags", ctypes.c_ushort),
                ("fAnyOperationsAborted", ctypes.c_bool),
                ("hNameMappings", ctypes.c_void_p),
                ("lpszProgressTitle", ctypes.c_wchar_p),
            ]

        FO_DELETE = 0x0003
        FOF_SILENT = 0x0004
        FOF_NOCONFIRMATION = 0x0010
        FOF_ALLOWUNDO = 0x0040
        source = path + "\0\0"
        operation = SHFILEOPSTRUCTW(
            None, FO_DELETE, source, None,
            FOF_SILENT | FOF_NOCONFIRMATION | FOF_ALLOWUNDO,
            False, None, None
        )
        result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(operation))
        return result == 0 and not operation.fAnyOperationsAborted
