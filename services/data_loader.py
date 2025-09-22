import pandas as pd
import numpy as np
from .utils import jalali_to_gregorian

COLUMNS_TO_READ = [
    "کد", "شماره چک", "تاریخ سررسید", "مبلغ", "موقعیت جغرافیایی چک",
    "وضعیت 1", "اجرائیات", "تاریخ آخرین وضعیت", "تاریخ وصول", "تاریخ دریافت",
    "بانک", "استان", "تاریخ ایجاد", "تاریخ آخرین نماچک", "پاسخ نماچک",
    "وضعیت نهایی", "وصول کننده", "مسئول وصول", "نوع وصول",
    "نوع درخواست", "تاریخ پیگیری"
]

def load_data(path="data.xlsx", sheet="data"):
    df = pd.read_excel(path, sheet_name=sheet, usecols=COLUMNS_TO_READ)
    df = df.where(pd.notnull(df), None)  # clean NaN

    # Convert all date columns
    date_columns = [
        "تاریخ سررسید",
        "تاریخ آخرین وضعیت",
        "تاریخ وصول",
        "تاریخ دریافت",
        "تاریخ ایجاد",
        "تاریخ آخرین نماچک",
        "تاریخ پیگیری"
    ]

    # 3️⃣ Replace placeholders with NaN
    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].replace({'0': np.nan, '': np.nan, '0/0/0': np.nan})

    # 4️⃣ Convert Jalali → Gregorian and ensure datetime
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col].apply(jalali_to_gregorian),
                                     errors='coerce',
                                     format='%Y/%m/%d')

    df = df[df['کد'] > 60000]
    df["مبلغ"] = pd.to_numeric(df["مبلغ"], errors="coerce").fillna(0)

    # Ensure column exists with safe dtype
    df["تاریخ پیگیری تا وصول"] = pd.Series(dtype="Int64")

    # شرط پایه: اگر تاریخ پیگیری خالی است
    mask_no_followup = df["تاریخ پیگیری"].isna()
    df.loc[mask_no_followup, "مسئول پیگیری"] = "صندوق"
    df.loc[mask_no_followup, "تاریخ پیگیری تا وصول"] = 0

    # شرط ۱: تاریخ وصول notna و اختلاف با تاریخ پیگیری در بازه ±30 روز
    cond1 = (
        df["تاریخ وصول"].notna()
        & df["تاریخ پیگیری"].notna()
        & (df["تاریخ پیگیری"] - df["تاریخ وصول"]).dt.days.between(-30, 30)
    )

    # شرط ۲: تاریخ وصول na و اختلاف تاریخ پیگیری و تاریخ آخرین وضعیت در بازه ±30 روز
    cond2 = (
        df["تاریخ وصول"].isna()
        & df["تاریخ پیگیری"].notna()
        & (df["تاریخ پیگیری"] - df["تاریخ آخرین وضعیت"]).dt.days.between(-30, 30)
    )

    # اعمال مسئول پیگیری فقط روی رکوردهایی که تاریخ پیگیری دارند
    df.loc[~mask_no_followup, "مسئول پیگیری"] = np.where(
        (cond1 | cond2)[~mask_no_followup],
        df.loc[~mask_no_followup, "مسئول وصول"],
        "صندوق",
    )

    # تاریخ پیگیری تا وصول
    df.loc[~mask_no_followup & df["تاریخ وصول"].notna(), "تاریخ پیگیری تا وصول"] = (
        (df["تاریخ پیگیری"] - df["تاریخ وصول"]).dt.days
    )

    df.loc[~mask_no_followup & df["تاریخ وصول"].isna(), "تاریخ پیگیری تا وصول"] = (
        (df["تاریخ پیگیری"] - df["تاریخ آخرین وضعیت"]).dt.days
    )

    return df
