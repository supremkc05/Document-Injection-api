from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import BookingRequest, BookingResponse, BookingMetadata
from app.services.booking_service import BookingService

router = APIRouter(prefix="/api", tags=["Bookings"])


@router.post("/bookings", response_model=BookingResponse)
async def create_booking(
    request: BookingRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new interview booking
    
    - **name**: Name of the person booking
    - **email**: Email address
    - **date**: Booking date in YYYY-MM-DD format
    - **time**: Booking time in HH:MM format
    
    Returns:
    - **booking_id**: Unique identifier for the booking
    - **status**: Status of the operation
    """
    try:
        service = BookingService(db)
        booking_id = service.create_booking(
            name=request.name,
            email=request.email,
            date=request.date,
            time=request.time
        )

        return BookingResponse(
            booking_id=booking_id,
            status="created"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating booking: {str(e)}"
        )


@router.get("/bookings/{booking_id}", response_model=BookingMetadata)
async def get_booking(
    booking_id: str,
    db: Session = Depends(get_db)
):
    """
    Get booking details by ID
    
    - **booking_id**: Unique booking identifier
    """
    try:
        service = BookingService(db)
        booking = service.get_booking(booking_id)
        
        if not booking:
            raise HTTPException(
                status_code=404,
                detail=f"Booking {booking_id} not found"
            )
        
        return BookingMetadata.model_validate(booking)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving booking: {str(e)}"
        )


@router.get("/bookings", response_model=List[BookingMetadata])
async def list_bookings(
    db: Session = Depends(get_db)
):
    """
    List all bookings
    """
    try:
        service = BookingService(db)
        bookings = service.list_bookings()
        return [BookingMetadata.model_validate(b) for b in bookings]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing bookings: {str(e)}"
        )


@router.delete("/bookings/{booking_id}")
async def delete_booking(
    booking_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a booking
    
    - **booking_id**: Unique booking identifier
    """
    try:
        service = BookingService(db)
        success = service.delete_booking(booking_id)
        
        if success:
            return {"status": "success", "message": f"Booking {booking_id} deleted"}
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Booking {booking_id} not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting booking: {str(e)}"
        )
