import numpy as np
import jdatetime
import pandas as pd

def to_python_type(value):
    """Recursively convert numpy/pandas types to native Python types"""
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, pd.Series):   # <---- add this
        return value.tolist()
    if isinstance(value, pd.DataFrame):  # optional: handle whole DataFrames
        return value.to_dict(orient="records")
    if isinstance(value, (dict,)):
        return {k: to_python_type(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_python_type(v) for v in value]
    return value



def calculate_and_respond(func, df, *args, **kwargs):
    result = func(df, *args, **kwargs)
    return to_python_type(result)

# تبدیل تاریخ شمسی به میلادی
def jalali_to_gregorian(sh_date):
    if pd.isna(sh_date):  # Check if the value is NaN or black
        return np.nan  # Return NaN for missing values and blanks
    try:
        year, month, day = map(int, sh_date.split('/'))
        gregorian_date = jdatetime.date(year, month, day).togregorian()
        return gregorian_date  # This is a datetime.date object (no time component)
    except (ValueError, AttributeError):
        return np.nan  # Return NaN for invalid or unparseable dates

def safe_divide(a, b):
    """Divide a by b safely, return 0 if b is 0 or None."""
    try:
        if b in [0, None, np.nan]:
            return 0
        return a / b
    except Exception:
        return 0