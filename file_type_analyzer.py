import os


class FileTypeAnalyzer:

    CATEGORIES = {

        "Images": {
            ".jpg", ".jpeg", ".png", ".gif", ".bmp",
            ".webp", ".tiff", ".tif", ".svg", ".ico",
            ".heic", ".heif", ".raw", ".cr2", ".nef",
            ".arw", ".orf", ".dng", ".psd"
        },

        "Videos": {
            ".mp4", ".mkv", ".avi", ".mov", ".wmv",
            ".flv", ".webm", ".mpeg", ".mpg", ".m4v",
            ".3gp", ".3g2", ".ts", ".mts", ".m2ts",
            ".vob", ".ogv", ".rm", ".rmvb"
        },

        "Documents": {
            ".pdf", ".doc", ".docx", ".docm", ".txt",
            ".rtf", ".md", ".tex", ".xls", ".xlsx",
            ".xlsm", ".xltx", ".csv", ".ods", ".ppt",
            ".pptx", ".pptm", ".odp", ".odt", ".pages",
            ".epub", ".mobi"
        },

        "Audio": {
            ".mp3", ".wav", ".aac", ".flac", ".ogg",
            ".oga", ".m4a", ".wma", ".opus", ".amr",
            ".aiff", ".aif", ".mid", ".midi", ".mka"
        },

        "Archives": {
            ".zip", ".rar", ".7z", ".tar", ".gz",
            ".bz2", ".xz", ".iso"
        },

        "Programs": {
            ".py", ".java", ".c", ".cpp", ".h",
            ".html", ".htm", ".css", ".js", ".php",
            ".sql", ".json", ".xml", ".bat", ".cmd",
            ".exe", ".msi", ".dll"
        }
    }

    def get_category(self, extension):

        extension = extension.lower()

        for category, extensions in self.CATEGORIES.items():

            if extension in extensions:
                return category

        return "Others"

    def analyze(self, files):

        result = {}

        for file in files:

            extension = os.path.splitext(
                file.get("name", "")
            )[1].lower()

            if extension == "":
                extension = "No Extension"

            category = self.get_category(extension)

            if category not in result:

                result[category] = {
                    "count": 0,
                    "size": 0
                }

            result[category]["count"] += 1
            result[category]["size"] += file.get(
                "size", 0
            )

        return result

    def analyze_extensions(self, files):

        extension_data = {}

        for file in files:

            extension = os.path.splitext(
                file.get("name", "")
            )[1].lower()

            if extension == "":
                extension = "No Extension"

            if extension not in extension_data:

                extension_data[extension] = {
                    "count": 0,
                    "size": 0,
                    "category": self.get_category(
                        extension
                    )
                }

            extension_data[extension]["count"] += 1

            extension_data[extension]["size"] += (
                file.get("size", 0)
            )

        return extension_data

    def get_largest_types(self, files, limit=10):

        extension_data = self.analyze_extensions(files)

        result = []

        for extension, data in extension_data.items():

            result.append({
                "extension": extension,
                "category": data["category"],
                "count": data["count"],
                "size": data["size"]
            })

        result.sort(
            key=lambda item: item["size"],
            reverse=True
        )

        return result[:limit]