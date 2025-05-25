import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class TestTaskManagerApp:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup Chrome driver"""
        print("Setting up Selenium WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        
        # Use localhost since your app is running locally
        self.base_url = "http://localhost:5000"
        print(f"✓ WebDriver setup complete. Testing URL: {self.base_url}")
        
        yield
        
        self.driver.quit()
        print("✓ WebDriver cleanup complete")

    def test_homepage_loads(self):
        """Test Case 1: Verify homepage loads correctly"""
        print("\n=== Test Case 1: Homepage Load ===")
        
        self.driver.get(self.base_url)
        
        # Check title
        assert "Task Manager" in self.driver.title
        print("✓ Page title correct")
        
        # Check main heading
        heading = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        assert "Task List" in heading.text
        print("✓ Main heading found")
        
        # Check Add Task button
        add_button = self.driver.find_element(By.ID, "add-task-btn")
        assert add_button.is_displayed()
        print("✓ Add Task button visible")
        
        print("✅ Homepage load test PASSED")

    def test_add_task_functionality(self):
        """Test Case 2: Verify adding a new task works correctly"""
        print("\n=== Test Case 2: Add Task Functionality ===")
        
        self.driver.get(self.base_url)
        
        # Click Add Task button
        add_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "add-task-btn"))
        )
        add_button.click()
        print("✓ Clicked Add Task button")
        
        # Fill form
        title_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "title"))
        )
        description_field = self.driver.find_element(By.ID, "description")
        
        test_title = f"Selenium Test Task {int(time.time())}"
        test_description = "This task was created by Selenium automation"
        
        title_field.send_keys(test_title)
        description_field.send_keys(test_description)
        print("✓ Filled form fields")
        
        # Submit form
        submit_button = self.driver.find_element(By.ID, "submit-btn")
        submit_button.click()
        print("✓ Submitted form")
        
        # Wait for redirect and check result
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # Check if task appears or success message shows
        page_source = self.driver.page_source
        success = test_title in page_source or "successfully" in page_source.lower()
        
        assert success, "Task was not added successfully"
        print("✓ Task added successfully")
        
        print("✅ Add task functionality test PASSED")

    def test_navigation_functionality(self):
        """Test Case 3: Verify navigation works correctly"""
        print("\n=== Test Case 3: Navigation Functionality ===")
        
        self.driver.get(self.base_url)
        
        # Navigate to Add Task via navbar
        nav_add_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Add Task"))
        )
        nav_add_link.click()
        print("✓ Clicked navigation Add Task link")
        
        # Verify we're on add task page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "title"))
        )
        assert "Add New Task" in self.driver.page_source
        print("✓ Successfully navigated to Add Task page")
        
        # Navigate back to Home
        nav_home_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Home"))
        )
        nav_home_link.click()
        print("✓ Clicked navigation Home link")
        
        # Verify we're back on homepage
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "add-task-btn"))
        )
        assert "Task List" in self.driver.page_source
        print("✓ Successfully navigated back to homepage")
        
        print("✅ Navigation functionality test PASSED")

if __name__ == "__main__":
    print("Running Selenium Tests...")
    pytest.main([__file__, "-v", "-s"]) 