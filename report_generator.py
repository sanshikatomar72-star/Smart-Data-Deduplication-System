import csv
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


class ReportGenerator:

    def __init__(self, report_folder="reports"):

        self.report_folder = report_folder

        os.makedirs(
            self.report_folder,
            exist_ok=True
        )

    def _create_filename(self, extension):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        return os.path.join(
            self.report_folder,
            f"deduplication_report_{timestamp}.{extension}"
        )

    def format_size(self, size):

        if size < 1024:
            return f"{size:.2f} B"

        if size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"

        if size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"

        return f"{size / (1024 * 1024 * 1024):.2f} GB"

    def generate_csv_report(
        self,
        folder_path,
        files,
        duplicate_groups,
        storage_wasted,
        potential_saving,
        saving_percentage,
        folder_analysis=None,
        extension_analysis=None,
        priority_results=None
    ):

        file_path = self._create_filename("csv")

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as csv_file:

            writer = csv.writer(csv_file)

            writer.writerow([
                "SMART DATA DEDUPLICATION "
                "AND STORAGE OPTIMIZATION SYSTEM"
            ])

            writer.writerow([])

            writer.writerow([
                "Scan Folder",
                folder_path
            ])

            writer.writerow([
                "Report Date",
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ])

            writer.writerow([
                "Total Files",
                len(files)
            ])

            writer.writerow([
                "Duplicate Groups",
                len(duplicate_groups)
            ])

            duplicate_file_count = sum(
                max(0, len(group["files"]) - 1)
                for group in duplicate_groups
            )

            writer.writerow([
                "Duplicate Files",
                duplicate_file_count
            ])

            writer.writerow([
                "Storage Wasted",
                self.format_size(storage_wasted)
            ])

            writer.writerow([
                "Potential Saving",
                self.format_size(potential_saving)
            ])

            writer.writerow([
                "Saving Percentage",
                f"{saving_percentage:.2f}%"
            ])

            writer.writerow([])

            writer.writerow([
                "FILE DETAILS"
            ])

            writer.writerow([
                "File Name",
                "Folder",
                "Extension",
                "Size",
                "Path"
            ])

            for file in files:

                writer.writerow([
                    file.get("name", ""),
                    file.get("folder", ""),
                    file.get("extension", ""),
                    self.format_size(
                        file.get("size", 0)
                    ),
                    file.get("path", "")
                ])

            writer.writerow([])

            if folder_analysis:

                writer.writerow([
                    "FOLDER-WISE ANALYSIS"
                ])

                writer.writerow([
                    "Folder",
                    "Files",
                    "Size"
                ])

                for folder, data in folder_analysis.items():

                    writer.writerow([
                        folder,
                        data.get("files", 0),
                        self.format_size(
                            data.get("size", 0)
                        )
                    ])

                writer.writerow([])

            if extension_analysis:

                writer.writerow([
                    "FILE-TYPE ANALYSIS"
                ])

                writer.writerow([
                    "Extension",
                    "Category",
                    "Files",
                    "Size"
                ])

                for extension, data in extension_analysis.items():

                    writer.writerow([
                        extension,
                        data.get("category", "Others"),
                        data.get("count", 0),
                        self.format_size(
                            data.get("size", 0)
                        )
                    ])

                writer.writerow([])

            if priority_results:

                writer.writerow([
                    "DUPLICATE PRIORITY ANALYSIS"
                ])

                writer.writerow([
                    "Rank",
                    "Priority",
                    "Files",
                    "Wasted Storage",
                    "Waste Share"
                ])

                for item in priority_results:

                    writer.writerow([
                        item.get("rank", ""),
                        item.get("priority", ""),
                        item.get("file_count", 0),
                        self.format_size(
                            item.get(
                                "wasted_storage",
                                0
                            )
                        ),
                        f"{item.get('waste_share', 0):.2f}%"
                    ])

        return file_path

    def generate_pdf_report(
        self,
        folder_path,
        files,
        duplicate_groups,
        storage_wasted,
        potential_saving,
        saving_percentage,
        folder_analysis=None,
        extension_analysis=None,
        priority_results=None,
        ram_before=None,
        ram_peak=None,
        ram_after=None,
        scan_time=None
    ):

        file_path = self._create_filename("pdf")

        document = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=35,
            leftMargin=35,
            topMargin=35,
            bottomMargin=35
        )

        styles = getSampleStyleSheet()

        story = []

        title = Paragraph(
            "<b>Smart Data Deduplication and "
            "Storage Optimization System</b>",
            styles["Title"]
        )

        story.append(title)
        story.append(Spacer(1, 12))

        story.append(
            Paragraph(
                "<b>Scan Folder:</b> "
                + str(folder_path),
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                "<b>Report Date:</b> "
                + datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                styles["Normal"]
            )
        )

        story.append(Spacer(1, 15))

        duplicate_file_count = sum(
            max(0, len(group["files"]) - 1)
            for group in duplicate_groups
        )

        summary_data = [
            ["Metric", "Value"],
            [
                "Total Files",
                str(len(files))
            ],
            [
                "Duplicate Groups",
                str(len(duplicate_groups))
            ],
            [
                "Duplicate Files",
                str(duplicate_file_count)
            ],
            [
                "Storage Wasted",
                self.format_size(storage_wasted)
            ],
            [
                "Potential Saving",
                self.format_size(potential_saving)
            ],
            [
                "Saving Percentage",
                f"{saving_percentage:.2f}%"
            ]
        ]

        if scan_time is not None:

            summary_data.append([
                "Scan Time",
                f"{scan_time:.2f} seconds"
            ])

        if ram_before is not None:

            summary_data.append([
                "RAM Before Scan",
                f"{ram_before:.2f}%"
            ])

        if ram_peak is not None:

            summary_data.append([
                "Peak RAM Usage",
                f"{ram_peak:.2f}%"
            ])

        if ram_after is not None:

            summary_data.append([
                "RAM After Scan",
                f"{ram_after:.2f}%"
            ])

        summary_table = Table(
            summary_data,
            colWidths=[2.8 * inch, 2.5 * inch]
        )

        summary_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#172554")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        story.append(
            Paragraph(
                "<b>SCAN SUMMARY</b>",
                styles["Heading2"]
            )
        )

        story.append(summary_table)
        story.append(Spacer(1, 18))

        if folder_analysis:

            story.append(
                Paragraph(
                    "<b>FOLDER-WISE ANALYSIS</b>",
                    styles["Heading2"]
                )
            )

            folder_data = [
                ["Folder", "Files", "Size"]
            ]

            for folder, data in folder_analysis.items():

                folder_data.append([
                    str(folder),
                    str(data.get("files", 0)),
                    self.format_size(
                        data.get("size", 0)
                    )
                ])

            folder_table = Table(
                folder_data,
                colWidths=[
                    3.4 * inch,
                    1.0 * inch,
                    1.4 * inch
                ]
            )

            folder_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#2563eb")
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    )
                ])
            )

            story.append(folder_table)
            story.append(Spacer(1, 18))

        if extension_analysis:

            story.append(
                Paragraph(
                    "<b>FILE-TYPE ANALYSIS</b>",
                    styles["Heading2"]
                )
            )

            extension_data = [
                [
                    "Extension",
                    "Category",
                    "Files",
                    "Size"
                ]
            ]

            for extension, data in extension_analysis.items():

                extension_data.append([
                    str(extension),
                    str(
                        data.get(
                            "category",
                            "Others"
                        )
                    ),
                    str(
                        data.get(
                            "count",
                            0
                        )
                    ),
                    self.format_size(
                        data.get(
                            "size",
                            0
                        )
                    )
                ])

            extension_table = Table(
                extension_data,
                colWidths=[
                    1.1 * inch,
                    2.0 * inch,
                    1.0 * inch,
                    1.7 * inch
                ]
            )

            extension_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#0891b2")
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    )
                ])
            )

            story.append(extension_table)
            story.append(Spacer(1, 18))

        if priority_results:

            story.append(
                Paragraph(
                    "<b>DUPLICATE PRIORITY ANALYSIS</b>",
                    styles["Heading2"]
                )
            )

            priority_data = [
                [
                    "Rank",
                    "Priority",
                    "Files",
                    "Wasted",
                    "Share"
                ]
            ]

            for item in priority_results:

                priority_data.append([
                    str(
                        item.get(
                            "rank",
                            ""
                        )
                    ),
                    str(
                        item.get(
                            "priority",
                            ""
                        )
                    ),
                    str(
                        item.get(
                            "file_count",
                            0
                        )
                    ),
                    self.format_size(
                        item.get(
                            "wasted_storage",
                            0
                        )
                    ),
                    f"{item.get('waste_share', 0):.2f}%"
                ])

            priority_table = Table(
                priority_data,
                colWidths=[
                    0.6 * inch,
                    1.2 * inch,
                    0.8 * inch,
                    1.7 * inch,
                    1.2 * inch
                ]
            )

            priority_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#7c3aed")
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    )
                ])
            )

            story.append(priority_table)
            story.append(Spacer(1, 18))

        story.append(
            Paragraph(
                "<b>Generated by Smart Data "
                "Deduplication and Storage "
                "Optimization System</b>",
                styles["Normal"]
            )
        )

        document.build(story)

        return file_path