
from pathlib import Path
import pandas as pd

# Find the project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

# Find CSV files inside the data folder
csv_files = list(DATA_DIR.glob("*.csv"))

if not csv_files:
    print("ERROR: No CSV file found inside the data folder.")
else:
    csv_path = csv_files[0]
    print("CSV filename:", csv_path.name)

    # Load the CSV into a Pandas DataFrame
    df = pd.read_csv(csv_path)

    print("\nDataset shape (rows, columns):")
    print(df.shape)

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nMissing values in each column:")
    print(df.isnull().sum())

    print("\nData types:")
    print(df.dtypes)



    print("\nRows with missing values:")
    print(df[df.isnull().any(axis=1)].to_string(index=False))

    print("\nTransaction status counts:")
    print(df["Status"].value_counts().to_string())

    print("\nDate range:")
    dates = pd.to_datetime(df["Order_date"], dayfirst=True, errors="coerce")
    print("Earliest:", dates.min())
    print("Latest:", dates.max())

    print("\nQuantity and price summary:")
    print(df[["Quantity", "Unit_price", "Discount_amount"]].describe())
