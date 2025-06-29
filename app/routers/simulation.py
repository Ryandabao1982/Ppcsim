from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import datetime # Import datetime
from app import crud, models, schemas, auth
from app.database import get_db
from app.simulation_logic import run_weekly_simulation

router = APIRouter(
    prefix="/api/simulate",
    tags=["Simulation"],
    dependencies=[Depends(auth.get_current_user)] # All simulation routes require authentication
)

@router.post("/advance-week", status_code=status.HTTP_200_OK)
def advance_simulation_week(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Advances the simulation by one week.
    This will trigger the generation of impressions, clicks, sales, etc.,
    based on the current campaign setups.
    """
    try:
        # For MVP, we'll use today's date as the start of the simulated week.
        # A more advanced system would track a `current_simulation_date` for the user.
        # This date represents the beginning of the week for which metrics are generated.
        sim_start_date_for_week = datetime.date.today() # Or retrieve from user's profile/simulation state

        run_weekly_simulation(db=db, user=current_user, current_sim_date=sim_start_date_for_week)

        return {"message": f"Simulation advanced by one week for user {current_user.username} starting {sim_start_date_for_week}. Performance data generated."}
    except Exception as e:
        # Log the exception e (ideally using a proper logger)
        print(f"Error during simulation for user {current_user.username}: {e}") # Basic print for now
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred during simulation: {str(e)}")

# Ensure this router is added to the main app in app/main.py
# from app.routers import simulation as simulation_router
# app.include_router(simulation_router.router)
