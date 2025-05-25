CREATE DATABASE IF NOT EXISTS taskmanager;
USE taskmanager;

CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data for testing
INSERT INTO tasks (title, description, status) VALUES
('Sample Task 1', 'This is a sample task for testing', 'pending'),
('Sample Task 2', 'Another sample task', 'completed'),
('Setup Database', 'Configure MySQL database for the application', 'completed'); 