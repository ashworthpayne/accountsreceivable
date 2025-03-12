from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routers import companies, system_settings, financial_data, invoices, inventory, customers, auth

app = FastAPI(title="Severson Products API")

# ✅ Allow frontend (React) to make API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ✅ React frontend
    allow_credentials=True,
    allow_methods=["*"],  # ✅ Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # ✅ Allow all headers
)

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(companies.router, prefix="/api", tags=["Companies"])
app.include_router(system_settings.router, prefix="/api", tags=["System Settings"])
app.include_router(financial_data.router, prefix="/api", tags=["Financial Data"])
app.include_router(invoices.router, prefix="/api", tags=["Invoices"])
app.include_router(inventory.router, prefix="/api", tags=["Inventory"])
app.include_router(customers.router, prefix="/api", tags=["Customers"])  # ✅ Attach router with /api prefix


@app.get("/")
def home():
    return {"message": "Welcome to Severson Products API"}
