from unittest.mock import patch, MagicMock
import pytest
from app.maps_service import find_nearby
from app.exceptions import MapsAPIError

@patch("app.maps_service.get_maps_api_key")
@patch("app.maps_service.httpx.get")
def test_find_nearby_success(mock_get, mock_get_key):
    """Test find_nearby successfully parses places."""
    mock_get_key.return_value = "fake_key"
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "status": "OK",
        "results": [
            {
                "name": "General Hospital",
                "vicinity": "123 Main St",
                "geometry": {"location": {"lat": 10.0, "lng": 20.0}},
                "rating": 4.5
            }
        ]
    }
    mock_get.return_value = mock_response

    places = find_nearby(10.0, 20.0, "hospital")
    assert len(places) == 1
    assert places[0].name == "General Hospital"
    assert places[0].lat == 10.0
    assert places[0].rating == 4.5

@patch("app.maps_service.get_maps_api_key")
@patch("app.maps_service.httpx.get")
def test_find_nearby_api_error(mock_get, mock_get_key):
    """Test find_nearby raises MapsAPIError on failed API requests."""
    mock_get_key.return_value = "fake_key"
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "status": "REQUEST_DENIED",
        "error_message": "Invalid API Key"
    }
    mock_get.return_value = mock_response

    with pytest.raises(MapsAPIError, match="REQUEST_DENIED"):
        find_nearby(10.0, 20.0, "hospital")

@patch("app.maps_service.get_maps_api_key")
def test_find_nearby_missing_key(mock_get_key):
    """Test find_nearby returns empty list if API key is missing."""
    mock_get_key.return_value = None
    places = find_nearby(10.0, 20.0, "hospital")
    assert places == []
