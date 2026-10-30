from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal, init_db_schema
from backend.app.routers import auth, simulation, vendors, crm, manufacturing, accounting, hr, inventory, tenants
from backend.app.routers import settings as settings_router
from backend.app.seed import seed_database
from backend.app.services.tenant_service import seed_multi_tenants

# Create DB tables & sync schema
init_db_schema()

# Auto seed database on startup if empty
seed_database()

# Ensure multi-tenant companies exist
startup_db = SessionLocal()
try:
    seed_multi_tenants(startup_db)
finally:
    startup_db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Virtual Lab & Simulation Platform for Enterprise Resource Planning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(simulation.router, prefix=settings.API_V1_STR)
app.include_router(vendors.router, prefix=settings.API_V1_STR)
app.include_router(crm.router, prefix=settings.API_V1_STR)
app.include_router(manufacturing.router, prefix=settings.API_V1_STR)
app.include_router(accounting.router, prefix=settings.API_V1_STR)
app.include_router(hr.router, prefix=settings.API_V1_STR)
app.include_router(inventory.router, prefix=settings.API_V1_STR)
app.include_router(tenants.router, prefix=settings.API_V1_STR)
app.include_router(settings_router.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": "VLab-ERP: Virtual Lab & Business Simulation Engine",
        "status": "operational",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health")
@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    db = SessionLocal()
    try:
        from backend.app.models.models import Company, User, Product, Vendor
        co_count = db.query(Company).count()
        usr_count = db.query(User).count()
        prod_count = db.query(Product).count()
        ven_count = db.query(Vendor).count()
        return {
            "status": "healthy",
            "database": "connected",
            "db_path": str(settings.DATABASE_URL),
            "stats": {
                "companies": co_count,
                "users": usr_count,
                "products": prod_count,
                "vendors": ven_count
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "error",
            "detail": str(e)
        }
    finally:
        db.close()

