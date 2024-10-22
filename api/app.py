from fastapi import FastAPI, File, UploadFile, Form
from .staff import staff_router
from .zone import zone_router

# Initialize FastAPI app
app = FastAPI()
# Add routers to the main FastAPI app
app.include_router(staff_router)
app.include_router(zone_router)



