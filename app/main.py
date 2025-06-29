from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles # Import StaticFiles
from fastapi.responses import FileResponse # To serve index.html from root
from sqlalchemy.orm import Session
from datetime import timedelta
import os # For path joining

from app import crud, models, schemas, auth # models needed for Base.metadata.create_all if used
from app.database import SessionLocal, engine, get_db
from app.config import settings

# If not using Alembic for table creation initially (e.g. for quick dev setup)
# models.Base.metadata.create_all(bind=engine) # Creates tables if they don't exist

app = FastAPI(title="Amazon Ads Simulator API", version="0.1.0")

# Authentication Router (can be moved to a separate file later e.g. app/routers/auth.py)
auth_router = FastAPI() # Using a sub-application/router for auth routes

@auth_router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user_by_username = crud.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@auth_router.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Include the auth router in the main app
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])


# Example of a protected endpoint
@app.get("/api/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    # In Pydantic v2, models.User might not be directly usable as response_model if it's a SQLAlchemy model.
    # It's better to use schemas.User here.
    # For now, this will work as FastAPI can convert it.
    return current_user

@app.get("/")
def read_root():
    return {"message": "Welcome to the Amazon Ads Simulator API"}

# Placeholder for other routers (campaigns, products, etc.)
from app.routers import campaigns as campaigns_router
from app.routers import simulation as simulation_router
from app.routers import dashboard as dashboard_router
from app.routers import reports as reports_router
# from app.routers import products as products_router # Example

app.include_router(campaigns_router.router)
app.include_router(simulation_router.router)
app.include_router(dashboard_router.router)
app.include_router(reports_router.router)
# app.include_router(products_router.router)

# Mount static files directory (CSS, JS, images for frontend)
# Ensure the 'static' directory exists at the root of your project (same level as 'app' directory)
# If 'static' is inside 'app', the path would be "app/static"
# Assuming 'static' is at the project root:
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if not os.path.exists(static_dir):
    # Fallback if running from within app dir or static is nested differently
    # This might happen in some execution contexts.
    # A more robust solution would use settings or ensure consistent CWD.
    alt_static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(alt_static_dir):
        static_dir = alt_static_dir
    else: # If it truly doesn't exist, create it for placeholder files
        os.makedirs(static_dir, exist_ok=True)
        print(f"Created static directory at: {static_dir} as it was not found.")


app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=FileResponse, include_in_schema=False)
async def read_index():
    index_html_path = os.path.join(static_dir, "index.html")
    if not os.path.exists(index_html_path):
        # Create a placeholder index.html if it doesn't exist
        placeholder_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Ads Sim API</title></head>
        <body>
            <h1>Welcome to Amazon Ads Simulator API</h1>
            <p>API is running. Frontend placeholder.</p>
            <ul>
                <li><a href="/static/auth.html">Login/Register</a></li>
                <li><a href="/static/dashboard.html">Dashboard</a></li>
                <li><a href="/static/campaigns.html">Campaigns</a></li>
                <li><a href="/static/str.html">Search Term Report</a></li>
            </ul>
        </body>
        </html>
        """
        with open(index_html_path, "w") as f:
            f.write(placeholder_content)
        print(f"Created placeholder index.html at: {index_html_path}")
    return FileResponse(index_html_path)


# To run this app (from the project root):
# uvicorn app.main:app --reload
