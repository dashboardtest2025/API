# services/calculations/calc_province_table.py
import pandas as pd
from services.utils import jalali_to_gregorian, safe_divide

def calc_province_table(df: pd.DataFrame, start_date: str, end_date: str, out_path: str = "province_table.xlsx"):
    # 1. Convert Jalali → Gregorian
    start = pd.to_datetime(jalali_to_gregorian(start_date), errors="coerce")
    end = pd.to_datetime(jalali_to_gregorian(end_date), errors="coerce")

    # 2. Ensure مبلغ is numeric
    df["مبلغ"] = pd.to_numeric(df["مبلغ"], errors="coerce").fillna(0)

    # 3. Container
    records = []

    provinces = df["استان"].dropna().unique()

    for prov in provinces:
        df_prov = df[df["استان"] == prov]

        # ایجاد برگشتی
        create_back = df_prov[
            (df_prov["تاریخ ایجاد"].between(start, end))
            | (df_prov["تاریخ ایجاد"].isna() & df_prov["تاریخ دریافت"].between(start, end))
        ]["مبلغ"].sum()

        # وصول
        vosol = df_prov[
            (df_prov["وضعیت نهایی"] == "وصول")
            & (
                (df_prov["تاریخ وصول"].between(start, end))
                | (df_prov["تاریخ وصول"].isna() & df_prov["تاریخ آخرین وضعیت"].between(start, end))
            )
        ]["مبلغ"].sum()

        # نسبت وصول به ایجاد برگشتی
        ratio_vosol_create = safe_divide(vosol, create_back) * 100

        # برگشتی بر اساس سررسید
        return_due = df_prov[df_prov["تاریخ سررسید"].between(start, end)]["مبلغ"].sum()

        # وصول بر اساس سررسید
        vosol_due = df_prov[
            (df_prov["وضعیت نهایی"] == "وصول")
            & (df_prov["تاریخ سررسید"].between(start, end))
        ]["مبلغ"].sum()

        # مانده برگشتی بر اساس سررسید
        remain_due = df_prov[
            (df_prov["وضعیت نهایی"] == "وصول نشده")
            & (df_prov["تاریخ سررسید"].between(start, end))
        ]["مبلغ"].sum()

        # درصد وصول بر اساس سررسید
        perc_vosol_due = safe_divide(vosol_due, return_due) * 100

        # درصد مانده برگشتی بر اساس سررسید
        perc_remain_due = safe_divide(remain_due, return_due) * 100

        records.append({
            "استان": prov,
            "ایجاد برگشتی": create_back,
            "وصول": vosol,
            "نسبت وصول به ایجاد برگشتی": ratio_vosol_create,
            "برگشتی بر اساس سررسید": return_due,
            "وصول بر اساس سررسید": vosol_due,
            "مانده برگشتی بر اساس سررسید": remain_due,
            "درصد وصول بر اساس سررسید": perc_vosol_due,
            "درصد مانده برگشتی بر اساس سررسید": perc_remain_due,
        })

    # DataFrame
    df_result = pd.DataFrame(records).set_index("استان")

    # Totals row
    totals = df_result.sum(numeric_only=True)
    totals.name = "جمع کل"
    # fix % recalculations
    totals["نسبت وصول به ایجاد برگشتی"] = safe_divide(totals["وصول"], totals["ایجاد برگشتی"]) * 100
    totals["درصد وصول بر اساس سررسید"] = safe_divide(totals["وصول بر اساس سررسید"], totals["برگشتی بر اساس سررسید"]) * 100
    totals["درصد مانده برگشتی بر اساس سررسید"] = safe_divide(totals["مانده برگشتی بر اساس سررسید"], totals["برگشتی بر اساس سررسید"]) * 100
    df_result = pd.concat([df_result, totals.to_frame().T])

    # Export
    df_result.to_excel(out_path)

    return df_result.reset_index().to_dict(orient="records")
