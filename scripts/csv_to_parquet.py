"""
===============================================================================
CSV TO PARQUET CONVERTER
===============================================================================

DESCRIPTION:
    Converts any .csv file into a compressed .parquet file located in the 
    exact same folder as the source file.

USAGE / COMMAND:
    Open Terminal, navigate to the folder containing your script or target file,
    and run:

        python3 csv_to_parquet.py "path/to/your_file.csv"

OUTPUT:
    Generates a file with the identical name and path, ending in .parquet:
    Example Input:  "Documents/Flight Data/flight.csv"
    Example Output: "Documents/Flight Data/flight.parquet"
===============================================================================
"""

import sys
from pathlib import Path
import pandas as pd

def convert_csv_to_parquet():
    # 1. Verify a file argument was passed
    if len(sys.argv) < 2:
        print("Error: Missing input CSV file.")
        print('Usage: python3 csv_to_parquet.py "filename.csv"')
        sys.exit(1)

    # 2. Extract and parse the input path
    csv_path = Path(sys.argv[1])

    # 3. Check if the input CSV actually exists
    if not csv_path.exists():
        print(f"Error: File not found at '{csv_path}'")
        sys.exit(1)

    # 4. Construct the output Parquet path in the exact same directory
    parquet_path = csv_path.with_suffix('.parquet')

    print(f"Reading CSV: {csv_path.name}...")
    
    # Read CSV and export to Parquet
    df = pd.read_csv(csv_path)
    df.to_parquet(parquet_path, engine='pyarrow')

    # Calculate compression ratio for confirmation
    csv_size_mb = csv_path.stat().st_size / (1024 * 1024)
    parquet_size_mb = parquet_path.stat().st_size / (1024 * 1024)
    reduction = (1 - (parquet_size_mb / csv_size_mb)) * 100 if csv_size_mb > 0 else 0

    print(f"Success! Created: {parquet_path}")
    print(f"File size reduced from {csv_size_mb:.2f} MB to {parquet_size_mb:.2f} MB ({reduction:.1f}% reduction).")

if __name__ == '__main__':
    convert_csv_to_parquet()