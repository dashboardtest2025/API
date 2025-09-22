# app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from services.data_loader import load_data
import services.calculations as calculations
from services.utils import calculate_and_respond

app = FastAPI(title="Finance Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # for testing, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your main dataframe once
df = load_data()


@app.get("/")
def root():
    return {
        "message": "Finance Dashboard API is running!",
        "available_functions": [f for f in dir(calculations) if not f.startswith("_")]
    }


@app.get("/calculate")
async def calculate_get(request: Request):
    """
    Example:
      GET /calculate?function=total_amount&date=1402/06/10
    """
    params = dict(request.query_params)
    function_name = params.pop("function", None)

    if not function_name:
        raise HTTPException(status_code=400, detail="Missing 'function' parameter.")

    if not hasattr(calculations, function_name):
        raise HTTPException(status_code=404, detail=f"Function '{function_name}' not found.")

    func = getattr(calculations, function_name)
    try:
        result = calculate_and_respond(func, df, **params)
        return {"function": function_name, "params": params, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calculate")
async def calculate_post(request: Request):
    """
    Example JSON body:
    {
      "function": "total_amount",
      "params": { "date": "1402/06/10", "province": "تهران" }
    }
    """
    body = await request.json()
    function_name = body.get("function")
    params = body.get("params", {})

    if not function_name:
        raise HTTPException(status_code=400, detail="Missing 'function' in request body.")

    if not hasattr(calculations, function_name):
        raise HTTPException(status_code=404, detail=f"Function '{function_name}' not found.")

    func = getattr(calculations, function_name)
    try:
        result = calculate_and_respond(func, df, **params)
        return {"function": function_name, "params": params, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dashboard")
async def dashboard(request: Request):
    body = await request.json()
    start_date = body.get("start_date")
    end_date = body.get("end_date")

    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail="Missing dates")

    # get_dashboard_data فعلا در حالت تست است
    result = get_dashboard_data(df, start_date, end_date)
    return result
