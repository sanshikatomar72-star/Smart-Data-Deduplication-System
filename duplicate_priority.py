class DuplicatePriorityAnalyzer:

    def analyze(self, duplicate_groups):

        group_data = []

        for group in duplicate_groups:

            files = group.get("files", [])

            if len(files) < 2:
                continue

            wasted_storage = sum(
                file.get("size", 0)
                for file in files[1:]
            )

            group_size = sum(
                file.get("size", 0)
                for file in files
            )

            group_data.append({
                "hash": group.get("hash", ""),
                "files": files,
                "file_count": len(files),
                "group_size": group_size,
                "wasted_storage": wasted_storage
            })

        total_wasted = sum(
            item["wasted_storage"]
            for item in group_data
        )

        group_data.sort(
            key=lambda item: item["wasted_storage"],
            reverse=True
        )

        results = []

        for rank, item in enumerate(
            group_data,
            start=1
        ):

            if total_wasted > 0:

                waste_share = (
                    item["wasted_storage"]
                    / total_wasted
                ) * 100

            else:
                waste_share = 0

            if waste_share >= 50:
                priority = "High"

            elif waste_share >= 10:
                priority = "Medium"

            else:
                priority = "Low"

            results.append({
                "rank": rank,
                "priority": priority,
                "file_count": item["file_count"],
                "group_size": item["group_size"],
                "wasted_storage": item["wasted_storage"],
                "waste_share": waste_share,
                "files": item["files"],
                "hash": item["hash"]
            })

        return results

    def get_priority_count(self, priority_results):

        counts = {
            "High": 0,
            "Medium": 0,
            "Low": 0
        }

        for item in priority_results:

            priority = item["priority"]

            if priority in counts:
                counts[priority] += 1

        return counts

    def get_high_priority_groups(
        self,
        priority_results
    ):

        return [
            item
            for item in priority_results
            if item["priority"] == "High"
        ]

    def get_medium_priority_groups(
        self,
        priority_results
    ):

        return [
            item
            for item in priority_results
            if item["priority"] == "Medium"
        ]

    def get_low_priority_groups(
        self,
        priority_results
    ):

        return [
            item
            for item in priority_results
            if item["priority"] == "Low"
        ]