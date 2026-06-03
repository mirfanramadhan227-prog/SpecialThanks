import pandas as pd

import os
from datetime import datetime
from pathlib import Path

from modules.database import engine

def backup_current_data():

    backup_folder = "backup"

    os.makedirs(
        backup_folder,
        exist_ok=True
    )

    try:

        old_df = pd.read_sql(
            "SELECT * FROM client_project",
            engine
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        backup_file = os.path.join(
            backup_folder,
            f"client_project_{timestamp}.xlsx"
        )

        old_df.to_excel(
            backup_file,
            index=False
        )

        return backup_file

    except Exception:

        # jika tabel belum ada
        return None

def cleanup_old_backups():

    backup_folder = "backup"

    if not os.path.exists(backup_folder):
        return

    files = [

        os.path.join(
            backup_folder,
            f
        )

        for f in os.listdir(
            backup_folder
        )

        if f.endswith(".xlsx")

    ]

    files.sort(
        key=os.path.getmtime,
        reverse=True
    )

    keep_files = 30

    for old_file in files[keep_files:]:

        try:

            os.remove(old_file)

        except Exception:
            pass

def generate_changelog(old_df, new_df):

    changelog_dir = "changelog"

    Path(changelog_dir).mkdir(
        exist_ok=True
    )

    timestamp = datetime.now()

    old_rows = len(old_df)
    new_rows = len(new_df)

    # =====================
    # RECORD LEVEL CHANGES
    # =====================

    old_records = set(

        zip(
            old_df["Client"].astype(str).str.strip(),
            old_df["Commodity"].astype(str).str.strip(),
            old_df["kabupaten"].astype(str).str.strip()
        )

    )

    new_records = set(

        zip(
            new_df["Client"].astype(str).str.strip(),
            new_df["Commodity"].astype(str).str.strip(),
            new_df["kabupaten"].astype(str).str.strip()
        )

    )

    added_records = sorted(
        new_records - old_records
    )

    removed_records = sorted(
        old_records - new_records
    )

    # =====================
    # CLIENT
    # =====================

    old_clients = set(
        old_df["Client"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    new_clients = set(
        new_df["Client"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    added_clients = sorted(
        new_clients - old_clients
    )

    removed_clients = sorted(
        old_clients - new_clients
    )

    # =====================
    # COMMODITY
    # =====================

    old_commodity = set(
        old_df["Commodity"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    new_commodity = set(
        new_df["Commodity"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    added_commodity = sorted(
        new_commodity - old_commodity
    )

    removed_commodity = sorted(
        old_commodity - new_commodity
    )

    # =====================
    # KABUPATEN
    # =====================

    old_kab = set(
        old_df["kabupaten"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    new_kab = set(
        new_df["kabupaten"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    added_kab = sorted(
        new_kab - old_kab
    )

    removed_kab = sorted(
        old_kab - new_kab
    )

    report = []

    report.append(
        "=" * 50
    )

    report.append(
        f"UPLOAD : {timestamp}"
    )

    report.append(
        "=" * 50
    )

    report.append("")
    report.append(
        f"Rows Lama : {old_rows}"
    )

    report.append(
        f"Rows Baru : {new_rows}"
    )

    report.append(
        f"Added Rows : {max(0, new_rows - old_rows)}"
    )

    report.append(
        f"Deleted Rows : {max(0, old_rows - new_rows)}"
    )

    report.append("")

    report.append(
        "CLIENT BARU"
    )

    report.append(
        "-" * 30
    )

    report.extend(
        added_clients or ["Tidak ada"]
    )

    report.append("")

    report.append(
        "CLIENT DIHAPUS"
    )

    report.append(
        "-" * 30
    )

    report.extend(
        removed_clients or ["Tidak ada"]
    )

    report.append("")

    report.append(
        "COMMODITY BARU"
    )

    report.append(
        "-" * 30
    )

    report.extend(
        added_commodity or ["Tidak ada"]
    )

    report.append("")

    report.append(
        "COMMODITY DIHAPUS"
    )

    report.append(
        "-" * 30
    )

    report.extend(
        removed_commodity or ["Tidak ada"]
    )

    report.append("")

    report.append(
        "KABUPATEN BARU"
    )

    report.append(
        "-" * 30
    )

    report.extend(
        added_kab or ["Tidak ada"]
    )

    report.append("")

    report.append(
        "KABUPATEN DIHAPUS"
    )

    report.append(
        "-" * 30
    )

    report.extend(
        removed_kab or ["Tidak ada"]
    )

    report.append("")
    report.append(
        "DETAIL RECORD BARU"
    )

    report.append(
        "-" * 30
    )

    if added_records:

        for rec in added_records:

            report.append(
                f"{rec[0]} | {rec[1]} | {rec[2]}"
            )

    else:

        report.append(
            "Tidak ada"
        )

    report.append("")

    report.append(
        "DETAIL RECORD DIHAPUS"
    )

    report.append(
        "-" * 30
    )

    if removed_records:

        for rec in removed_records:

            report.append(
                f"{rec[0]} | {rec[1]} | {rec[2]}"
            )

    else:

        report.append(
            "Tidak ada"
        )

    filename = os.path.join(
        changelog_dir,
        f"changelog_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(report)
        )

    return filename

def import_excel_to_postgres(filepath):

    try:

        old_df = pd.read_sql(
            "SELECT * FROM client_project",
            engine
        )

    except Exception:

        old_df = pd.DataFrame()

    backup_current_data()

    cleanup_old_backups()

    new_df = pd.read_excel(filepath)

    if not old_df.empty:

        generate_changelog(
            old_df,
            new_df
        )

    new_df.to_sql(
        "client_project",
        engine,
        if_exists="replace",
        index=False
    )

    return len(new_df)