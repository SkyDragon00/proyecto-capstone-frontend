import pytest
import httpx
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app


class TestProfileOperations:
    """Test class for profile update and delete operations."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_settings(self):
        """Mock settings object."""
        mock = MagicMock()
        mock.API_URL = "http://test-api.com"
        return mock

    def test_update_profile_assistant_success(self, client, mock_settings):
        """Test successful assistant profile update."""
        with patch('main.httpx.AsyncClient') as mock_client:
            # Mock the user info response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": 1,
                "role": "assistant",
                "first_name": "John",
                "last_name": "Doe"
            }
            
            # Mock the update response
            mock_update_response = MagicMock()
            mock_update_response.status_code = 200
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value.patch.return_value = mock_update_response
            
            # Test data
            form_data = {
                "first_name": "John Updated",
                "phone": "555-123-4567",
                "gender": "male"
            }
            
            with patch('main.SettingsDependency', return_value=mock_settings):
                response = client.post(
                    "/profile/update",
                    data=form_data,
                    cookies={"access_token": "test_token"}
                )
            
            assert response.status_code == 303
            assert response.headers["location"] == "/profile"

    def test_update_profile_unauthorized(self, client, mock_settings):
        """Test profile update with unauthorized token."""
        with patch('main.httpx.AsyncClient') as mock_client:
            # Mock unauthorized response
            mock_response = MagicMock()
            mock_response.status_code = 401
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            form_data = {
                "first_name": "John Updated"
            }
            
            with patch('main.SettingsDependency', return_value=mock_settings):
                response = client.post(
                    "/profile/update",
                    data=form_data,
                    cookies={"access_token": "invalid_token"}
                )
            
            assert response.status_code == 303
            assert response.headers["location"] == "/login"

    def test_delete_profile_success(self, client, mock_settings):
        """Test successful profile deletion."""
        with patch('main.httpx.AsyncClient') as mock_client:
            # Mock the user info response
            mock_info_response = MagicMock()
            mock_info_response.status_code = 200
            mock_info_response.json.return_value = {
                "id": 1,
                "role": "assistant"
            }
            
            # Mock the delete response
            mock_delete_response = MagicMock()
            mock_delete_response.status_code = 204
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_info_response
            mock_client.return_value.__aenter__.return_value.delete.return_value = mock_delete_response
            
            with patch('main.SettingsDependency', return_value=mock_settings):
                response = client.delete(
                    "/profile",
                    headers={"accept": "application/json"},
                    cookies={"access_token": "test_token"}
                )
            
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["message"] == "Perfil eliminado con éxito"

    def test_delete_profile_redirect_on_normal_request(self, client, mock_settings):
        """Test profile deletion redirects on normal (non-AJAX) requests."""
        with patch('main.httpx.AsyncClient') as mock_client:
            # Mock the user info response
            mock_info_response = MagicMock()
            mock_info_response.status_code = 200
            mock_info_response.json.return_value = {
                "id": 1,
                "role": "assistant"
            }
            
            # Mock the delete response
            mock_delete_response = MagicMock()
            mock_delete_response.status_code = 204
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_info_response
            mock_client.return_value.__aenter__.return_value.delete.return_value = mock_delete_response
            
            with patch('main.SettingsDependency', return_value=mock_settings):
                response = client.delete(
                    "/profile",
                    cookies={"access_token": "test_token"}
                )
            
            assert response.status_code == 303
            assert response.headers["location"] == "/logout"

    def test_profile_update_no_data_provided(self, client, mock_settings):
        """Test profile update with no data provided."""
        with patch('main.SettingsDependency', return_value=mock_settings):
            response = client.post(
                "/profile/update",
                data={},  # Empty data
                cookies={"access_token": "test_token"}
            )
        
        assert response.status_code == 400

    def test_profile_update_staff_role(self, client, mock_settings):
        """Test profile update for staff role."""
        with patch('main.httpx.AsyncClient') as mock_client:
            # Mock the user info response for staff
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": 1,
                "role": "staff",
                "first_name": "Jane",
                "last_name": "Smith"
            }
            
            # Mock the update response
            mock_update_response = MagicMock()
            mock_update_response.status_code = 200
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value.patch.return_value = mock_update_response
            
            form_data = {
                "first_name": "Jane Updated",
                "email": "jane.updated@example.com"
            }
            
            with patch('main.SettingsDependency', return_value=mock_settings):
                response = client.post(
                    "/profile/update",
                    data=form_data,
                    cookies={"access_token": "test_token"}
                )
            
            assert response.status_code == 303
            assert response.headers["location"] == "/profile"

    def test_profile_update_organizer_role(self, client, mock_settings):
        """Test profile update for organizer role."""
        with patch('main.httpx.AsyncClient') as mock_client:
            # Mock the user info response for organizer
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": 1,
                "role": "organizer",
                "first_name": "Bob",
                "last_name": "Johnson"
            }
            
            # Mock the update response
            mock_update_response = MagicMock()
            mock_update_response.status_code = 200
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value.patch.return_value = mock_update_response
            
            form_data = {
                "first_name": "Bob Updated",
                "last_name": "Johnson Updated"
            }
            
            with patch('main.SettingsDependency', return_value=mock_settings):
                response = client.post(
                    "/profile/update",
                    data=form_data,
                    cookies={"access_token": "test_token"}
                )
            
            assert response.status_code == 303
            assert response.headers["location"] == "/profile"


if __name__ == "__main__":
    pytest.main([__file__])
