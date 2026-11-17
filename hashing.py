import hashlib
import os


class HashCalculator:

    def __init__(self):
        self.chunk_size = 1024 * 1024

    def calculate_hash(self, file_path):

        sha256 = hashlib.sha256()

        try:

            if not os.path.isfile(file_path):
                return None

            with open(
                file_path,
                "rb"
            ) as file:

                while True:

                    data = file.read(
                        self.chunk_size
                    )

                    if not data:
                        break

                    sha256.update(data)

            return sha256.hexdigest()

        except (
            PermissionError,
            OSError
        ):

            return None

    def calculate_hash_with_size(
        self,
        file_path
    ):

        try:

            if not os.path.isfile(file_path):
                return None

            file_size = os.path.getsize(
                file_path
            )

            file_hash = self.calculate_hash(
                file_path
            )

            if file_hash is None:
                return None

            return {
                "path": file_path,
                "size": file_size,
                "hash": file_hash
            }

        except (
            PermissionError,
            OSError
        ):

            return None

    def verify_same_hash(
        self,
        file1,
        file2
    ):

        hash1 = self.calculate_hash(
            file1
        )

        hash2 = self.calculate_hash(
            file2
        )

        if hash1 is None or hash2 is None:
            return False

        return hash1 == hash2

    def get_hash_algorithm(self):

        return "SHA-256"

    def get_chunk_size(self):

        return self.chunk_size