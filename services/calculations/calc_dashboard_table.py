import pandas as pd
import numpy as np
from services.utils import jalali_to_gregorian, safe_divide, TARGET, OSTAN_PEYGIRI

COLUMN_RENAME = {
    "req_sar": "درخواست سرحسابی",
    "vos_sar": "وصول سرحسابی",
    "vos_cash": "وصول واریز نقدی",
    "vos_total": "وصول کل",
    "perc_success_sar": "درصد موفقیت وصول سرحسابی",
    "perc_vos_sar": "درصد وصول سرحسابی",
    "perc_vos_cash": "درصد وصول واریز نقدی",
    "vos_doc": "وصول سند شده",
    "vos_no_doc": "وصول سند نشده",
    "target": "پلن",
    "perc_target": "درصد تحقق پلن",
    "bargasht_no_doc": "برگشتی سند نشده",
    "bargasht_doc": "برگشتی سند شده",
    "bargasht_total": "برگشتی کل",
    "vos_distribution": "توزیع وصول",
    # new column mapping
    "ratio_return_to_collection": "نسبت وصول به برگشتی",
}


def calc_dashboard_table(df: pd.DataFrame, start_date: str, end_date: str, out_path: str = "dashboard_table.xlsx"):
    """
    Calculate dashboard performance table for each مسئول پیگیری and export to Excel.

    Returns:
        df_result (pd.DataFrame)
        result_dict (list of dicts for JSON)
    """

    # 1. Convert Jalali → Gregorian
    start = pd.to_datetime(jalali_to_gregorian(start_date), errors="coerce")
    end = pd.to_datetime(jalali_to_gregorian(end_date), errors="coerce")

    # 2. Ensure مبلغ is numeric
    df["مبلغ"] = pd.to_numeric(df["مبلغ"], errors="coerce").fillna(0)

    # 3. Prepare result container
    records = []

    # 4. Get all مسئول پیگیری
    responsibles = df["مسئول پیگیری"].dropna().unique()

    for res in responsibles:
        df_res = df[df["مسئول پیگیری"] == res]

        # (1) درخواست سرحسابی
        req_sar = df_res[
            (df_res["نوع درخواست"] == "سرحساب")
            & (df_res["تاریخ پیگیری"].between(start, end))
        ]["مبلغ"].sum()
        if res == "صندوق":
            req_sar = 0

        # (2) وصول سرحسابی
        vos_sar = df_res[
            (df_res["نوع وصول"] == "سرحساب")
            & (
                ((df_res["تاریخ وصول"].notna()) & (df_res["تاریخ وصول"].between(start, end)))
                | ((df_res["تاریخ وصول"].isna()) & (df_res["تاریخ آخرین وضعیت"].between(start, end)))
            )
        ]["مبلغ"].sum()

        # (3) وصول واریز نقدی
        vos_cash = df_res[
            (df_res["نوع وصول"] == "واریز نقدی")
            & (
                ((df_res["تاریخ وصول"].notna()) & (df_res["تاریخ وصول"].between(start, end)))
                | ((df_res["تاریخ وصول"].isna()) & (df_res["تاریخ آخرین وضعیت"].between(start, end)))
            )
        ]["مبلغ"].sum()

        # (4) وصول کل
        vos_total = vos_sar + vos_cash

        # (5) درصد موفقیت وصول سرحسابی
        perc_success_sar = safe_divide(vos_sar, req_sar) * 100

        # (6) درصد وصول سرحسابی
        perc_vos_sar = safe_divide(vos_sar, vos_total) * 100

        # (7) درصد وصول نقدی
        perc_vos_cash = safe_divide(vos_cash, vos_total) * 100

        # (8) وصول سند شده
        vos_doc = df_res[
            (df_res["وضعیت نهایی"] == "وصول")
            & (df_res["تاریخ وصول"].between(start, end))
        ]["مبلغ"].sum()

        # (9) وصول سند نشده
        vos_no_doc = df_res[
            (df_res["وضعیت نهایی"] == "وصول")
            & (df_res["تاریخ وصول"].isna())
            & (df_res["تاریخ آخرین وضعیت"].between(start, end))
        ]["مبلغ"].sum()

        # (10) پلن
        target = TARGET.get(res, 0)

        # (11) درصد تحقق پلن
        perc_target = safe_divide(vos_total, target) * 100

        # استان‌های مسئول پیگیری
        related_provinces = [ostan for ostan, r in OSTAN_PEYGIRI.items() if r == res]
        df_prov = df[df["استان"].isin(related_provinces)]

        # (12) برگشتی سند نشده
        bargasht_no_doc = df_prov[
            (df_prov["تاریخ ایجاد"].isna())
            & (df_prov["تاریخ دریافت"].between(start, end))
        ]["مبلغ"].sum()

        # (13) برگشتی سند شده
        bargasht_doc = df_prov[
            (df_prov["تاریخ ایجاد"].between(start, end))
        ]["مبلغ"].sum()

        # (14) برگشتی کل
        bargasht_total = bargasht_no_doc + bargasht_doc

        # (new) نسبت برگشتی به وصول = وصول کل / برگشتی کل * 100
        ratio_return_to_collection = safe_divide(vos_total, bargasht_total) * 100

        records.append({
            "responsible": res,
            "req_sar": req_sar,
            "vos_sar": vos_sar,
            "vos_cash": vos_cash,
            "vos_total": vos_total,
            "perc_success_sar": perc_success_sar,
            "perc_vos_sar": perc_vos_sar,
            "perc_vos_cash": perc_vos_cash,
            "vos_doc": vos_doc,
            "vos_no_doc": vos_no_doc,
            "target": target,
            "perc_target": perc_target,
            "bargasht_no_doc": bargasht_no_doc,
            "bargasht_doc": bargasht_doc,
            "bargasht_total": bargasht_total,
            "ratio_return_to_collection": ratio_return_to_collection,  # <-- new
        })

    # 5. Create DataFrame
    df_result = pd.DataFrame(records).set_index("responsible")

    # 6. Add total row
    totals = df_result.sum(numeric_only=True)
    totals.name = "جمع کل"
    # Fix % columns: recalc properly
    totals["perc_success_sar"] = safe_divide(totals["vos_sar"], totals["req_sar"]) * 100
    totals["perc_vos_sar"] = safe_divide(totals["vos_sar"], totals["vos_total"]) * 100
    totals["perc_vos_cash"] = safe_divide(totals["vos_cash"], totals["vos_total"]) * 100
    totals["perc_target"] = safe_divide(totals["vos_total"], totals["target"]) * 100
    # (new) total ratio recalc
    totals["ratio_return_to_collection"] = safe_divide(totals["vos_total"], totals["bargasht_total"]) * 100
    df_result = pd.concat([df_result, totals.to_frame().T])

    # (16) توزیع وصول
    grand_total = df_result.loc["جمع کل", "vos_total"]
    df_result["vos_distribution"] = safe_divide(df_result["vos_total"], grand_total) * 100

    # 7. Change the name of columns to persian (apply mapping)
    df_result = df_result.rename(columns=COLUMN_RENAME)

    # 8. Export to Excel
    df_result.to_excel(out_path)

    # 9. Return both formats
    return df_result.reset_index().to_dict(orient="records")
