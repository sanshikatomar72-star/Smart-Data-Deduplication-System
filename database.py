import sqlite3
import os
from datetime import datetime


class DatabaseManager:

    def __init__(self, db_path="database/deduplication.db"):

        self.db_path = db_path

        database_folder = os.path.dirname(self.db_path)

        if database_folder:
            os.makedirs(database_folder, exist_ok=True)

        self.create_database()
        self.migrate_database()

    def create_database(self):

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                scan_date TEXT NOT NULL,

                folder_path TEXT NOT NULL,

                total_files INTEGER,

                total_size INTEGER,

                duplicate_groups INTEGER DEFAULT 0,

                duplicate_files INTEGER DEFAULT 0,

                storage_wasted INTEGER DEFAULT 0,

                potential_saving INTEGER DEFAULT 0,

                saving_percentage REAL DEFAULT 0,

                skipped_files INTEGER DEFAULT 0,

                scan_time REAL DEFAULT 0

            )
        """)

        connection.commit()
        connection.close()

    def migrate_database(self):

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("PRAGMA table_info(scan_history)")

        existing_columns = {
            row[1]
            for row in cursor.fetchall()
        }

        required_columns = {

            "duplicate_groups":
                "INTEGER DEFAULT 0",

            "duplicate_files":
                "INTEGER DEFAULT 0",

            "storage_wasted":
                "INTEGER DEFAULT 0",

            "potential_saving":
                "INTEGER DEFAULT 0",

            "saving_percentage":
                "REAL DEFAULT 0",

            "skipped_files":
                "INTEGER DEFAULT 0",

            "scan_time":
                "REAL DEFAULT 0"
        }

        for column_name, column_type in required_columns.items():

            if column_name not in existing_columns:

                cursor.execute(
                    f"""
                    ALTER TABLE scan_history
                    ADD COLUMN {column_name} {column_type}
                    """
                )

        connection.commit()
        connection.close()

    def save_scan(
        self,
        folder_path,
        total_files,
        total_size,
        duplicate_groups,
        duplicate_files,
        storage_wasted,
        potential_saving,
        saving_percentage,
        skipped_files=0,
        scan_time=0
    ):

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO scan_history (

                scan_date,
                folder_path,
                total_files,
                total_size,
                duplicate_groups,
                duplicate_files,
                storage_wasted,
                potential_saving,
                saving_percentage,
                skipped_files,
                scan_time

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            folder_path,
            total_files,
            total_size,
            duplicate_groups,
            duplicate_files,
            storage_wasted,
            potential_saving,
            saving_percentage,
            skipped_files,
            scan_time
        ))

        connection.commit()
        connection.close()

    def get_scan_history(self):

        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()

        cursor.execute("""
            SELECT

                scan_date,
                folder_path,
                total_files,
                total_size,
                duplicate_groups,
                duplicate_files,
                storage_wasted,
                potential_saving,
                saving_percentage,
                skipped_files,
                scan_time

            FROM scan_history

            ORDER BY id DESC
        """)

        history = cursor.fetchall()

        connection.close()

        return history

    def get_latest_scan(self):

        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()

        cursor.execute("""
            SELECT *

            FROM scan_history

            ORDER BY id DESC

            LIMIT 1
        """)

        latest_scan = cursor.fetchone()

        connection.close()

        return latest_scan

    def clear_history(self):

        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM scan_history"
        )

        connection.commit()
        connection.close()