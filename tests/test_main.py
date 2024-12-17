import pytest
from unittest.mock import patch
from main import app, fetch_user, fetch_followers, fetch_following, USER_NOT_FOUND


# Fixture to create a test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# Mock response for successful user fetch
MOCK_USER_DATA = {
    "login": "testuser",
    "name": "Test User",
    "public_repos": 10,
    "followers": 20,
    "following": 15
}

# Mock response for followers
MOCK_FOLLOWERS = [{"login": f"follower{i}"} for i in range(3)]

# Mock response for following
MOCK_FOLLOWING = [{"login": f"following{i}"} for i in range(3)]


def mock_response(status_code=200, json_data=None):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data
    return MockResponse(json_data, status_code)


def test_home_page(client):
    """Test if home page renders"""
    response = client.get('/')
    assert response.status_code == 200


@patch('requests.get')
def test_fetch_user_success(mock_get):
    """Test successful user fetch"""
    mock_get.return_value = mock_response(200, MOCK_USER_DATA)
    result = fetch_user('testuser')
    assert result == MOCK_USER_DATA


@patch('requests.get')
def test_fetch_user_not_found(mock_get):
    """Test user not found"""
    mock_get.return_value = mock_response(404, None)
    result = fetch_user('nonexistentuser')
    assert result == USER_NOT_FOUND


@patch('requests.get')
def test_fetch_followers_success(mock_get):
    """Test successful followers fetch"""
    mock_get.return_value = mock_response(200, MOCK_FOLLOWERS)
    result = fetch_followers('testuser')
    assert result == ['follower0', 'follower1', 'follower2']


@patch('requests.get')
def test_fetch_followers_not_found(mock_get):
    """Test followers not found"""
    mock_get.return_value = mock_response(404, None)
    result = fetch_followers('nonexistentuser')
    assert result == USER_NOT_FOUND


@patch('requests.get')
def test_fetch_following_success(mock_get):
    """Test successful following fetch"""
    mock_get.return_value = mock_response(200, MOCK_FOLLOWING)
    result = fetch_following('testuser')
    assert result == ['following0', 'following1', 'following2']


@patch('requests.get')
def test_fetch_following_not_found(mock_get):
    """Test following not found"""
    mock_get.return_value = mock_response(404, None)
    result = fetch_following('nonexistentuser')
    assert result == USER_NOT_FOUND


@patch('main.fetch_user')
@patch('main.fetch_followers')
@patch('main.fetch_following')
def test_user_profile_success(mock_following, mock_followers, mock_user, client):
    """Test successful user profile fetch"""
    mock_user.return_value = MOCK_USER_DATA
    mock_followers.return_value = ['follower1', 'follower2']
    mock_following.return_value = ['following1', 'following2']
    response = client.get('/testuser')
    assert response.status_code == 200
    data = response.get_json()
    assert data['login'] == 'testuser'
    assert 'followers_list' in data
    assert 'following_list' in data


def test_user_profile_error(client):
    """Test user profile error handling"""
    response = client.get('/nonexistentuser')
    assert response.status_code == 200  # Flask returns 200 even for handled errors
    data = response.get_json()
    assert 'error' in data
    assert 'message' in data
    assert data['message'] == USER_NOT_FOUND
