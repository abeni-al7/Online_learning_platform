# Online Learning Platform
## By **Abenezer Alebachew Endalew**

Welcome to the Online Learning Platform! This platform is designed to provide a place where learners could find quality courses and teachers can upload the courses they prepare. Whether you are looking to develop new skills, enhance your knowledge, pursue a passion, or teach students our platform offers an easily accessible and user-friendly place to help you achieve your goals.

## How to run the app
To run the app, follow these steps:

1. **Clone the repository:**
    ```sh
    git clone https://github.com/abeni-al7/Online_learning_platform.git
    ```

2. **Navigate to the project directory:**
    ```sh
    cd Online_learning_platform
    ```

3. **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set environment variables for your database connection. (sqlite or Postgres)**
    Create a .env file and add your database connection string in the variable **DATABASE_URI**.

5. **Start the application:**
    ```sh
    python3 app.py
    ```

6. **Open your browser and go to:**
    ```
    http://localhost:5000
    ```

Now you should see the Online Learning Platform running locally on your machine.

## How to use the app
There is a simple user interface that guides anyone who wants to use the app to the place they want to go to.
Here is what you might do step by step

If you are a teacher:
1. **Register or Login as a teacher**
2. **Go to the profile page to edit or delete your profile**
3. **Go to the courses page to create new courses, update your courses and upload additional content to your existing courses. You can also delete your courses if you want**

If you are a student:
1. **Register or Login as a student**
2. **Go to the profile page to edit or delete your profile**
3. **Go to the courses page to access the courses that you are enrolled in, download the content uploaded to your course and unenroll from your existing courses. You can go to the browse courses page from there to see courses that are available for enrollment and look at their descriptions and choose to enroll into new courses.**

## Project Architecture

The project follows the following tech stack
### Frontend
- HTML
- Bootstrap

### Backend
- Python
- Flask
- SQLAlchemy

### Database
- SQLite (for development)
- PostgreSQL (for production) (when it is deployed)
