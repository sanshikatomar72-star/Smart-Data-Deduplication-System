from hashing import HashCalculator


class DuplicateDetector:

    def __init__(self):
        self.hash_calculator = HashCalculator()

    def find_duplicates(self, files):

        hash_groups = {}

        for file in files:

            file_hash = self.hash_calculator.calculate_hash(
                file["path"]
            )

            if file_hash is None:
                continue

            file["hash"] = file_hash

            if file_hash not in hash_groups:
                hash_groups[file_hash] = []

            hash_groups[file_hash].append(file)

        duplicate_groups = []

        for file_hash, group in hash_groups.items():

            if len(group) > 1:

                duplicate_groups.append({
                    "hash": file_hash,
                    "files": group
                })

        return duplicate_groups

    def get_duplicate_file_count(self, duplicate_groups):

        count = 0

        for group in duplicate_groups:

            files = group["files"]

            if len(files) > 1:
                count += len(files) - 1

        return count

    def get_duplicate_groups_count(self, duplicate_groups):

        return len(duplicate_groups)

    def get_duplicate_files(self, duplicate_groups):

        duplicate_files = []

        for group in duplicate_groups:

            files = group["files"]

            # First file is treated as the file to keep.
            for file in files[1:]:
                duplicate_files.append(file)

        return duplicate_files