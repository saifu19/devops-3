import pytest
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestTaskManagerApp:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup Chrome driver"""
        print("Setting up Selenium WebDriver...")
        
        # First, test connectivity to the Flask app
        self.base_url = os.environ.get('APP_URL', 'http://app:5000')
        self._wait_for_app()
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # More comprehensive SSL and security flags
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-certificate-errors-spki-list")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-popup-blocking")
        
        # Use explicit path to chromedriver
        service = Service('/usr/bin/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        yield
        
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def _wait_for_app(self):
        """Wait for the Flask app to be ready"""
        print(f"Waiting for app at {self.base_url} to be ready...")
        
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(self.base_url, timeout=5)
                if response.status_code == 200:
                    print(f"App is ready! Status: {response.status_code}")
                    return
                else:
                    print(f"App returned status {response.status_code}, retrying...")
            except requests.exceptions.RequestException as e:
                print(f"Attempt {i+1}/{max_retries}: {e}")
            
            time.sleep(2)
        
        raise Exception(f"App at {self.base_url} is not ready after {max_retries * 2} seconds")
    
    def test_homepage_loads(self):
        """Test that the homepage loads successfully"""
        print(f"Testing homepage at {self.base_url}")
        self.driver.get(self.base_url)
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check title
        assert "Task Manager" in self.driver.title
        print("Homepage loaded successfully")
    
    def test_add_task_functionality(self):
        """Test adding a new task"""
        print(f"Testing add task functionality at {self.base_url}/add")
        self.driver.get(f"{self.base_url}/add")
        
        # Wait for form to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "title"))
        )
        
        # Fill out the form
        title_field = self.driver.find_element(By.ID, "title")
        description_field = self.driver.find_element(By.ID, "description")
        submit_button = self.driver.find_element(By.ID, "submit-btn")
        
        title_field.send_keys("Selenium Test Task")
        description_field.send_keys("This is a test task created by Selenium")
        submit_button.click()
        
        # Check that we're redirected or see success message
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.current_url != f"{self.base_url}/add" or 
                          "success" in driver.page_source.lower() or
                          "added" in driver.page_source.lower()
        )
        
        print("Add task functionality test completed")
    
    def test_navigation_functionality(self):
        """Test navigation between pages"""
        print(f"Testing navigation functionality")
        
        # Start at homepage
        self.driver.get(self.base_url)
        
        # Wait for navigation to load
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Add Task"))
        )
        
        # Click on Add Task link
        add_task_link = self.driver.find_element(By.LINK_TEXT, "Add Task")
        add_task_link.click()
        
        # Verify we're on the add task page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        h1_text = self.driver.find_element(By.TAG_NAME, "h1").text
        assert "Add New Task" in h1_text
        
        print("Navigation functionality test completed")

if __name__ == "__main__":
    print("Running Selenium Tests...")
    pytest.main([__file__, "-v", "-s"]) 