"""
Main application file for the PhoneDash API.

This file initializes the FastAPI application, configures CORS, sets up the API
endpoints, and serves the frontend pages. It acts as the primary router,
delegating business logic to the services module.
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import pandas as pd
import io

from models import Phone, PhoneCreate, PhoneUpdate, ActionLog, PhonePage
from services import (
    create_phone,
    update_phone,
    delete_phone,
    list_phone_on_platform,
    search_and_filter_phones,
    update_platform_prices,
    bulk_upload_phones,
    get_dashboard_analytics,
    get_action_logs,
    bulk_list_on_platform,
)
from security import get_current_user

# Initialize the FastAPI application
app = FastAPI(
    title="Refurbished Phone Selling API",
    description="An API to manage and sell refurbished phones on multiple e-commerce platforms.",
    version="1.0.0",
)

# --- Static Files and Template Configuration ---
# Mount the 'static' directory to serve CSS, JS, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")
# Configure Jinja2 to look for templates in the 'templates' directory
templates = Jinja2Templates(directory="templates")

# --- CORS (Cross-Origin Resource Sharing) Middleware ---
# This allows the frontend (running on a different origin) to communicate with the backend.
origins = ["http://localhost", "http://localhost:8080", "http://127.0.0.1:5500", "null"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# --- Security and Authentication ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Page Rendering Endpoints ---


@app.get("/", include_in_schema=False)
async def serve_login(request: Request):
    """Serves the main login page (login.html)."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/app", include_in_schema=False)
async def serve_app(request: Request):
    """Serves the main application dashboard page (app.html)."""
    return templates.TemplateResponse("app.html", {"request": request})


# --- API Endpoints (JSON) ---


@app.get("/dashboard/analytics", tags=["Dashboard"])
def read_dashboard_analytics(
    brand: Optional[str] = None,
    condition: Optional[str] = None,
    platform: Optional[str] = None,
    current_user: str = Depends(get_current_user),
):
    """
    Retrieves and returns analytics data for the dashboard,
    optionally filtered by brand, condition, or platform.
    """
    return get_dashboard_analytics(brand, condition, platform)


@app.get("/logs", response_model=List[ActionLog], tags=["Logs"])
def read_action_logs(current_user: str = Depends(get_current_user)):
    """Retrieves and returns the list of all recorded user actions."""
    return get_action_logs()


@app.get("/phones", response_model=PhonePage, tags=["Inventory"])
def read_phones(
    brand: Optional[str] = None,
    condition: Optional[str] = None,
    platform: Optional[str] = None,
    skip: int = 0,
    limit: int = 15,
    current_user: str = Depends(get_current_user),
):
    """
    Retrieves a paginated and filtered list of phones from the inventory.
    """
    return search_and_filter_phones(brand, condition, platform, skip, limit)


@app.post("/phones", response_model=Phone, status_code=201, tags=["Inventory"])
def add_new_phone(phone: PhoneCreate, current_user: str = Depends(get_current_user)):
    """Adds a new phone to the inventory."""
    return create_phone(phone.dict())


@app.put("/phones/{phone_id}", response_model=Phone, tags=["Inventory"])
def update_existing_phone(
    phone_id: int,
    phone_update: PhoneUpdate,
    current_user: str = Depends(get_current_user),
):
    """Updates the details of an existing phone by its ID."""
    updated_phone = update_phone(phone_id, phone_update.dict(exclude_unset=True))
    if not updated_phone:
        raise HTTPException(status_code=404, detail="Phone not found")
    return updated_phone


@app.delete("/phones/{phone_id}", status_code=204, tags=["Inventory"])
def remove_phone(phone_id: int, current_user: str = Depends(get_current_user)):
    """Deletes a phone from the inventory by its ID."""
    if not delete_phone(phone_id):
        raise HTTPException(status_code=404, detail="Phone not found")
    # A 204 response should not have a body
    return None


@app.post("/phones/upload", tags=["Inventory"])
async def upload_phones_csv(
    file: UploadFile = File(...), current_user: str = Depends(get_current_user)
):
    """Allows bulk uploading of phone data from a CSV file."""
    contents = await file.read()
    try:
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        phones_data = df.to_dict(orient="records")
        bulk_upload_phones(phones_data)
        return {"message": f"{len(phones_data)} phones uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV file: {e}")


@app.post("/phones/bulk-list/{platform}", tags=["Platform Integration"])
def bulk_list_phones(
    platform: str,
    brand: Optional[str] = None,
    condition: Optional[str] = None,
    current_user: str = Depends(get_current_user),
):
    """Bulk lists all phones that match the filter criteria onto a specific platform."""
    return bulk_list_on_platform(platform, brand, condition)


@app.post("/phones/{phone_id}/list/{platform}", tags=["Platform Integration"])
def list_on_platform(
    phone_id: int, platform: str, current_user: str = Depends(get_current_user)
):
    """Simulates listing a single phone on a specific platform."""
    result = list_phone_on_platform(phone_id, platform)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/prices/update", tags=["Pricing"])
def update_all_prices(current_user: str = Depends(get_current_user)):
    """Triggers an automatic price update for all phones on all platforms."""
    update_platform_prices()
    return {"message": "All platform prices updated successfully"}


@app.post("/token", tags=["Authentication"])
def login_for_access_token(username: str = "admin", password: str = "password"):
    """
    Mock token endpoint for authentication. In a real application, this would
    validate user credentials against a database and issue a signed JWT.
    """
    if username == "admin" and password == "password":
        return {"access_token": "mock_token", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")


# --- Main Execution ---
if __name__ == "__main__":
    import uvicorn

    # This block allows running the server directly with `python main.py`
    uvicorn.run(app, host="0.0.0.0", port=8000)
