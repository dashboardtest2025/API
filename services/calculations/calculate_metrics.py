import pandas as pd
import numpy as np
from services.utils import jalali_to_gregorian, safe_divide, TARGET


def calculate_metrics(df: pd.DataFrame, start_date: str, end_date: str) -> dict:
    """
    Calculate financial metrics between two Jalali dates.
    start_date and end_date should be Jalali strings like '1402/06/10'.
    """

    # Convert Jalali → Gregorian → datetime
    start_date = pd.to_datetime(jalali_to_gregorian(start_date), errors="coerce")
    end_date = pd.to_datetime(jalali_to_gregorian(end_date), errors="coerce")

    # Ensure numeric مبلغ
    df["مبلغ"] = pd.to_numeric(df["مبلغ"], errors="coerce").fillna(0)

    # --- وصول سند شده ---
    vosool_sanad_shode = df[
        (df["وضعیت نهایی"] == "وصول")
        & (df["تاریخ وصول"].between(start_date, end_date))
    ]["مبلغ"].sum()

    # --- وصول سند نشده ---
    vosool_sanad_nashode = df[
        (df["وضعیت نهایی"] == "وصول")
        & (df["تاریخ وصول"].isna())
        & (df["تاریخ آخرین وضعیت"].between(start_date, end_date))
    ]["مبلغ"].sum()

    vosool_kol = vosool_sanad_shode + vosool_sanad_nashode

    # --- برگشتی سند شده ---
    bargashti_sanad_shode = df[
        (df["تاریخ ایجاد"].between(start_date, end_date))
    ]["مبلغ"].sum()

    # --- برگشتی سند نشده ---
    bargashti_sanad_nashode = df[
        (df["تاریخ ایجاد"].isna())
        & (df["تاریخ دریافت"].between(start_date, end_date))
    ]["مبلغ"].sum()

    bargashti_kol = bargashti_sanad_shode + bargashti_sanad_nashode

    # --- عملکردها ---
    performance_nashode = safe_divide(vosool_sanad_nashode, bargashti_kol) * 100
    performance_shode = safe_divide(vosool_sanad_shode, bargashti_kol) * 100

    # --- نحقق پلن کل ---
    performance_target = safe_divide(TARGET["وصول مطالبات"], bargashti_kol) * 100

    return {
        "total_collection": float(vosool_kol),
        "collection_documented": float(vosool_sanad_shode),
        "collection_not_documented": float(vosool_sanad_nashode),
        "total_returned": float(bargashti_kol),
        "returned_documented": float(bargashti_sanad_shode),
        "returned_not_documented": float(bargashti_sanad_nashode),
        "performance_not_documented": float(performance_nashode),
        "performance_documented": float(performance_shode),
        "performance_target": float(performance_target)
    }
