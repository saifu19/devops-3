from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql'),
    'database': os.getenv('DB_NAME', 'taskmanager'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'rootpassword'),
    'port': int(os.getenv('DB_PORT', 3306))
}


def wait_for_db():
    """Wait for database to be ready"""
    max_retries = 30
    retry_count = 0

    while retry_count < max_retries:
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            if connection.is_connected():
                connection.close()
                print("Database connection successful!")
                return True
        except Error as e:
            print(f"Database connection attempt {retry_count + 1} failed: {e}")
            retry_count += 1
            time.sleep(2)

    raise Exception("Could not connect to database after maximum retries")


def init_db():
    """Initialize the database with tasks table"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")

        # Create tasks table
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        cursor.execute(create_table_query)
        connection.commit()

        print("Database and table created successfully!")

    except Error as e:
        print(f"Error initializing database: {e}")
        raise e
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        raise e


@app.route('/')
def index():
    """Display all tasks"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
        tasks = cursor.fetchall()
        return render_template('index.html', tasks=tasks)
    except Error as e:
        flash(f'Database error: {e}')
        return render_template('index.html', tasks=[])
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/add', methods=['GET', 'POST'])
def add_task():
    """Add a new task"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        if not title:
            flash('Title is required!')
            return render_template('add_task.html')

        connection = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            insert_query = 'INSERT INTO tasks (title, description) VALUES (%s, %s)'
            cursor.execute(insert_query, (title, description))
            connection.commit()

            flash('Task added successfully!')
            return redirect(url_for('index'))

        except Error as e:
            flash(f'Error adding task: {e}')
            return render_template('add_task.html')
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    return render_template('add_task.html')


@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    """Mark task as completed"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        update_query = 'UPDATE tasks SET status = %s WHERE id = %s'
        cursor.execute(update_query, ('completed', task_id))
        connection.commit()

        flash('Task marked as completed!')

    except Error as e:
        flash(f'Error updating task: {e}')
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('index'))


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    """Delete a task"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        delete_query = 'DELETE FROM tasks WHERE id = %s'
        cursor.execute(delete_query, (task_id,))
        connection.commit()

        flash('Task deleted successfully!')

    except Error as e:
        flash(f'Error deleting task: {e}')
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('index'))


@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()

        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected' if result else 'disconnected'
        }
    except Error as e:
        return {
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'disconnected',
            'error': str(e)
        }, 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == '__main__':
    wait_for_db()
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
