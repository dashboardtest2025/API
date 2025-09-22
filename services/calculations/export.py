def export(df, path="exported_data.xlsx", sheet_name="Sheet1"):
    """
    Export a DataFrame to Excel for inspection.
    """
    df.to_excel(path, sheet_name=sheet_name, index=False)
    print(f"✅ DataFrame exported to {path}")