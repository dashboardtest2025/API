# services/calculations/get_dashboard_data.py
from services.calculations import calculate_metrics
from services.calculations.calc_dashboard_table import calc_dashboard_table
from services.calculations.calc_province_table import calc_province_table

def get_dashboard_data(df, start_date, end_date):
    # Calculate metrics
    metrics = calculate_metrics(df, start_date, end_date)
    
    # Calculate dashboard table
    dashboard_table = calc_dashboard_table(df, start_date, end_date)

    # Calculate Province Table
    province_table = calc_province_table(df, start_date, end_date)

    # Combine results into a single dictionary
    result = {
        "metrics": metrics,
        "dashboard_table": dashboard_table,
        "province_table": province_table
    }
    
    return result