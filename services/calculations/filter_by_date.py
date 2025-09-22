import pandas as pd
from services.utils import jalali_to_gregorian  # your existing function

def filter_by_date(df: pd.DataFrame, selected_date: str, column_name: str = "تاریخ سررسید"):
    """
    Filter df where column_name equals the selected date.
    selected_date is in Shamsi/Jalali.
    """
    # 1️⃣ Convert user input to Gregorian
    greg_date_str = jalali_to_gregorian(selected_date)
    
    # 2️⃣ Convert to pandas Timestamp
    greg_date = pd.to_datetime(greg_date_str, format="%Y/%m/%d", errors='coerce')
    
    if greg_date is pd.NaT:
        return {"error": "Invalid date input"}
    
    # 3️⃣ Filter the DataFrame
    filtered = df[df[column_name] == greg_date]
    
    # 4️⃣ Return as list or count
    return filtered.to_dict(orient="records")
