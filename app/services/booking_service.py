from sqlalchemy.orm import Session

from app.repositories.booking_repository import BookingRepository


class BookingService:
    """Service for handling interview bookings"""

    def __init__(self, db: Session):
        self.db = db
        self.booking_repo = BookingRepository(db)

    def create_booking(
        self,
        name: str,
        email: str,
        date: str,
        time: str
    ) -> str:
        """
        Create a new booking
        
        Args:
            name: Booking name
            email: Booking email
            date: Booking date (YYYY-MM-DD)
            time: Booking time (HH:MM)
            
        Returns:
            Booking ID
        """
        booking = self.booking_repo.create_booking(
            name=name,
            email=email,
            date=date,
            time=time
        )
        return booking.booking_id

    def get_booking(self, booking_id: str):
        """Get booking by ID"""
        return self.booking_repo.get_booking_by_id(booking_id)

    def list_bookings(self):
        """List all bookings"""
        return self.booking_repo.get_all_bookings()

    def get_bookings_by_email(self, email: str):
        """Get all bookings for a specific email"""
        return self.booking_repo.get_bookings_by_email(email)

    def delete_booking(self, booking_id: str) -> bool:
        """Delete a booking"""
        return self.booking_repo.delete_booking(booking_id)
