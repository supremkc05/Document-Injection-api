import pytest


class TestChatAPI:
    """Test chat API endpoints"""

    def test_chat_basic(self, client):
        """Test basic chat functionality"""
        chat_data = {
            "session_id": "test-session-1",
            "user_message": "Hello, how are you?"
        }
        
        response = client.post("/api/chat", json=chat_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "response" in data
        assert data["session_id"] == "test-session-1"

    def test_chat_empty_message(self, client):
        """Test chat with empty message"""
        chat_data = {
            "session_id": "test-session-2",
            "user_message": ""
        }
        
        response = client.post("/api/chat", json=chat_data)
        
        assert response.status_code == 400

    def test_chat_empty_session_id(self, client):
        """Test chat with empty session ID"""
        chat_data = {
            "session_id": "",
            "user_message": "Hello"
        }
        
        response = client.post("/api/chat", json=chat_data)
        
        assert response.status_code == 400

    def test_get_session_history(self, client):
        """Test retrieving session history"""
        session_id = "test-session-3"
        
        # Send a few messages
        for i in range(3):
            chat_data = {
                "session_id": session_id,
                "user_message": f"Message {i}"
            }
            client.post("/api/chat", json=chat_data)
        
        # Get history
        response = client.get(f"/api/chat/{session_id}/history")
        
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert data["session_id"] == session_id

    def test_clear_session(self, client):
        """Test clearing session history"""
        session_id = "test-session-4"
        
        # Send a message
        chat_data = {
            "session_id": session_id,
            "user_message": "Test message"
        }
        client.post("/api/chat", json=chat_data)
        
        # Clear session
        response = client.delete(f"/api/chat/{session_id}")
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
