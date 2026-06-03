from modules.upload_manager import import_excel_to_postgres

rows = import_excel_to_postgres(
    "data_backup.xlsx"
)

print(
    f"{rows} rows imported"
)