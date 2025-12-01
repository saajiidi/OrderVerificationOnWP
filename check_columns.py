import pandas as pd

# Read the Excel file
try:
    df = pd.read_excel('Sample.xlsx')
    print("Columns in your Excel file:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i}. {col}")
    
    print("\nFirst few rows of data:")
    print(df.head())
    
except Exception as e:
    print(f"Error reading Excel file: {e}")
