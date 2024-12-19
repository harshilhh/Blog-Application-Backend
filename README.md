# Blog-Application-Backend

## Project Overview

The CMS allows users to:
- Register and login with JWT token authentication.
- Create, update, view, and delete blogs.
    - Like and unlike blogs.
    - Access public and private posts with proper authorization checks.


### Technologies Used:
- **Flask** (API framework)
- **SQLite** (Database)
- **JWT** (Authentication)
- **SQLAlchemy** (ORM)


### API Endpoints

- **POST /accounts**: Create a new user account.
- **POST /accounts/login**: Login and get an authentication token.
- **PUT /accounts**: Update user details (authenticated users only).
- **DELETE /accounts**: Delete user account (authenticated users only).
- **GET /me**: Get information about the logged-in user.
- **POST /blog**: Create a new blog post.
- **GET /blog**: Get all blog posts.
- **GET /blog/{id}**: Get details of a specific blog post.
- **PUT /blog/{id}**: Update a specific blog post (only by the owner).
- **DELETE /blog/{id}**: Delete a specific blog post (only by the owner).
- **POST /like/{blog_id}**: Like a specific blog post.
- **DELETE /like/{blog_id}**: Unlike a specific blog post.

---


## Setup Instructions

### 1. Add the `.env` File
Create a `.env` file in the root directory and add the following configuration:

#### Redis Configuration
```
DB_URL="sqlite:///app.db"
SECRET_KEY="2kGm8U8FnVvq1Gn4lHvWl5y7V5db7JcGk6QzmHp2gR0"

```


### 2. Create a Virtual Environment and Install Requirements
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

3. Install all required libraries from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Run the Flask Application
In the first terminal, run the Flask application:
```bash
python3 run.py
```
The API should now be running locally at http://127.0.0.1:5000.



## Postman Collection

You can download the Postman collection for this project from the following link:

- [Download Postman Collection](./Blog%20Application.postman_collection)

