import pandas as pd
from sqlalchemy import create_engine

# =========================
# KONEKSI DATABASE
# =========================

engine = create_engine(
    "postgresql://postgres:Ramadhan10@localhost:5432/gis_dashboard"
)

# =========================
# BACA EXCEL
# =========================

from pathlib import Path

excel_file = Path(__file__).parent / "data_backup.xlsx"

df = pd.read_excel(excel_file)

# =========================
# IMPORT KE POSTGRESQL
# =========================

df.to_sql(
    "client_project",
    engine,
    if_exists="replace",
    index=False
)

print("IMPORT EXCEL BERHASIL!")