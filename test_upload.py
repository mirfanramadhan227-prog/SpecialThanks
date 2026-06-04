import pandas as pd
from modules.database import engine

df = pd.read_sql(
    "SELECT COUNT(*) FROM client_project",
    engine
)

print(df)