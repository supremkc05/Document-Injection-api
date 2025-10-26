import pytest
from app.schemas import BookingRequest


class TestBookingsAPI:
    """Test bookings API endpoints"""

    def test_create_booking(self, client):
        """Test creating a new booking"""
        booking_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "date": "2025-11-01",
            "time": "14:00"
        }
        
        response = client.post("/api/bookings", json=booking_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "booking_id" in data
        assert data["status"] == "created"

    def test_create_booking_invalid_email(self, client):
        """Test creating a booking with invalid email"""
        booking_data = {
            "name": "John Doe",
            "email": "invalid-email",
            "date": "2025-11-01",
            "time": "14:00"
        }
        
        response = client.post("/api/bookings", json=booking_data)
        
        assert response.status_code == 422  # Validation error

    def test_get_booking(self, client):
        """Test retrieving a booking"""
        # First create a booking
        booking_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "date": "2025-11-02",
            "time": "15:00"
        }
        create_response = client.post("/api/bookings", json=booking_data)
        booking_id = create_response.json()["booking_id"]
        
        # Then retrieve it
        response = client.get(f"/api/bookings/{booking_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["booking_id"] == booking_id
        assert data["name"] == "Jane Doe"
        assert data["email"] == "jane@example.com"

    def test_list_bookings(self, client):
        """Test listing all bookings"""
        # Create a few bookings
        for i in range(3):
            booking_data = {
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "date": "2025-11-01",
                "time": f"{10+i}:00"
            }
            client.post("/api/bookings", json=booking_data)
        
        # List bookings
        response = client.get("/api/bookings")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_delete_booking(self, client):
        """Test deleting a booking"""
        # Create a booking
        booking_data = {
            "name": "Test User",
            "email": "test@example.com",
            "date": "2025-11-01",
            "time": "12:00"
        }
        create_response = client.post("/api/bookings", json=booking_data)
        booking_id = create_response.json()["booking_id"]
        
        # Delete it
        response = client.delete(f"/api/bookings/{booking_id}")
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # Verify it's deleted
        get_response = client.get(f"/api/bookings/{booking_id}")
        assert get_response.status_code == 404
