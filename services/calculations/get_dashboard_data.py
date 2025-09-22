from services.calculations import calculate_metrics

def get_dashboard_data(df, start_date, end_date):
    return {
        "metrics": calculate_metrics(df, start_date, end_date)
        # "charts": {
        #     "daily_received": calc_daily_received_chart(df, start_date, end_date),
        #     "province_breakdown": calc_province_chart(df, start_date, end_date),
        # },
        # "tables": {
        #     "recent_transactions": calc_recent_table(df, start_date, end_date),
        #     "overdue_items": calc_overdue_table(df, start_date, end_date),
        # }
    }
