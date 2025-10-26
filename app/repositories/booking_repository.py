from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from app.database import Booking


class BookingRepository:
    """Repository for booking-related database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_booking(
        self,
        name: str,
        email: str,
        date: str,
        time: str
    ) -> Booking:
        """Create a new booking record"""
        booking = Booking(
            booking_id=str(uuid.uuid4()),
            name=name,
            email=email,
            date=date,
            time=time
        )
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def get_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        """Get booking by booking_id"""
        return self.db.query(Booking).filter(
            Booking.booking_id == booking_id
        ).first()

    def get_all_bookings(self) -> List[Booking]:
        """Get all bookings"""
        return self.db.query(Booking).all()

    def get_bookings_by_email(self, email: str) -> List[Booking]:
        """Get all bookings for a specific email"""
        return self.db.query(Booking).filter(
            Booking.email == email
        ).all()

    def delete_booking(self, booking_id: str) -> bool:
        """Delete a booking"""
        booking = self.get_booking_by_id(booking_id)
        if booking:
            self.db.delete(booking)
            self.db.commit()
            return True
        return False
