import pytest
import os
from app import app

# Use your local MySQL settings
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = 'rootpassword'  # Change this to your actual password
os.environ['DB_NAME'] = 'taskmanager'
os.environ['DB_PORT'] = '3306'

@pytest.fixture
def client():
    """Set up test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Test the index page loads correctly"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Task List' in rv.data
    print("✓ Index page test passed")

def test_add_task_page(client):
    """Test the add task page loads correctly"""
    rv = client.get('/add')
    assert rv.status_code == 200
    assert b'Add New Task' in rv.data
    print("✓ Add task page test passed")

def test_add_task_functionality(client):
    """Test adding a new task"""
    rv = client.post('/add', data={
        'title': 'Test Task',
        'description': 'Test Description'
    }, follow_redirects=True)
    assert rv.status_code == 200
    assert b'Test Task' in rv.data or b'Task added successfully' in rv.data
    print("✓ Add task functionality test passed")

def test_health_endpoint(client):
    """Test the health check endpoint"""
    rv = client.get('/health')
    assert rv.status_code in [200, 500]
    assert rv.is_json
    print("✓ Health endpoint test passed")

def test_add_task_empty_title(client):
    """Test adding a task with empty title fails"""
    rv = client.post('/add', data={
        'title': '',
        'description': 'Test Description'
    })
    assert rv.status_code == 200
    assert b'Title is required!' in rv.data
    print("✓ Empty title validation test passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 