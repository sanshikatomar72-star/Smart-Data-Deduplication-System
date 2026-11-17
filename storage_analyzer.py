class StorageAnalyzer:

    def calculate_storage_wasted(self, duplicate_groups):

        wasted_storage = 0

        for group in duplicate_groups:

            files = group["files"]

            if len(files) > 1:

                # First file is treated as the file to keep.
                for file in files[1:]:
                    wasted_storage += file["size"]

        return wasted_storage

    def calculate_potential_saving(self, duplicate_groups):

        return self.calculate_storage_wasted(duplicate_groups)

    def calculate_saving_percentage(
        self,
        total_size,
        potential_saving
    ):

        if total_size <= 0:
            return 0

        return (potential_saving / total_size) * 100

    def get_folder_duplicate_analysis(self, duplicate_groups):

        folder_data = {}

        for group in duplicate_groups:

            files = group["files"]

            if len(files) <= 1:
                continue

            # First file is kept.
            duplicate_files = files[1:]

            for file in duplicate_files:

                folder = file.get(
                    "folder",
                    "Unknown Folder"
                )

                if folder not in folder_data:

                    folder_data[folder] = {
                        "files": 0,
                        "wasted_storage": 0
                    }

                folder_data[folder]["files"] += 1

                folder_data[folder]["wasted_storage"] += (
                    file["size"]
                )

        return folder_data

    def get_largest_duplicate_groups(
        self,
        duplicate_groups,
        limit=10
    ):

        group_data = []

        for group in duplicate_groups:

            files = group["files"]

            if len(files) <= 1:
                continue

            wasted_storage = sum(
                file["size"]
                for file in files[1:]
            )

            group_data.append({
                "hash": group["hash"],
                "file_count": len(files),
                "wasted_storage": wasted_storage,
                "files": files
            })

        group_data.sort(
            key=lambda item: item["wasted_storage"],
            reverse=True
        )

        return group_data[:limit]

    def bytes_to_kb(self, size):

        return size / 1024

    def bytes_to_mb(self, size):

        return size / (1024 * 1024)

    def bytes_to_gb(self, size):

        return size / (1024 * 1024 * 1024)

    def format_size(self, size):

        if size < 1024:
            return f"{size:.2f} B"

        if size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"

        if size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"

        return f"{size / (1024 * 1024 * 1024):.2f} GB"