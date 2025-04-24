# RESTful-API-with-Authentication

# Task Management API

A secure backend API for task management applications, built with FastAPI and Python. This project demonstrates modern backend development practices including JWT authentication, RESTful API design, and database management.

## 🎯 What is this project?

This is a backend API (Application Programming Interface) that serves as the "engine" for task management applications. While it doesn't have a visual interface itself, it provides all the functionality needed for applications to manage users and their tasks.

Think of it like a restaurant kitchen - customers don't see it directly, but it prepares all the food (data) that gets served to them through waiters (frontend applications).

## 💡 Key Features

### User Management
- **User Registration**: Create new accounts with username, email, and password
- **Secure Authentication**: Login system with encrypted passwords and JWT tokens
- **Profile Management**: Users can update their information
- **Role-Based Access**: Admin users have additional privileges

### Task Management
- **Create Tasks**: Add new tasks with titles, descriptions, and priorities
- **View Tasks**: See all your tasks or filter by status/priority
- **Update Tasks**: Mark tasks as complete, change priorities, or edit details
- **Delete Tasks**: Remove tasks you no longer need
- **Task Organization**: Set due dates and categorize by priority (low, medium, high)

### Security Features
- **Password Encryption**: All passwords are securely hashed
- **JWT Authentication**: Secure token-based authentication system
- **Data Protection**: Users can only access their own tasks
- **Input Validation**: All data is validated before processing
- **Rate Limiting**: Protects against abuse and attacks

## 🚀 How to Use This API

### 1. Access the Documentation
Once the server is running, visit:
- Swagger UI: `http://your-server-address/docs`
- ReDoc: `http://your-server-address/redoc`

### 2. Basic Workflow
1. **Register a User**
   ```
   POST /api/auth/register
   {
     "username": "johndoe",
     "email": "john@example.com",
     "password": "SecurePass123!",
     "full_name": "John Doe"
   }
   ```

2. **Login**
   ```
   POST /api/auth/login
   {
     "username": "johndoe",
     "password": "SecurePass123!"
   }
   ```
   This returns a JWT token for authentication.

3. **Create a Task**
   ```
   POST /api/tasks/
   Headers: Authorization: Bearer <your_token>
   {
     "title": "Buy groceries",
     "description": "Milk, eggs, bread",
     "priority": "high",
     "due_date": "2024-05-01T10:00:00"
   }
   ```

4. **View Your Tasks**
   ```
   GET /api/tasks/
   Headers: Authorization: Bearer <your_token>
   ```

## 💻 Technical Details

### Technologies Used
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **SQLite**: Lightweight database (can be replaced with PostgreSQL)
- **Pydantic**: Data validation using Python type annotations
- **JWT**: JSON Web Tokens for secure authentication
- **Pytest**: Testing framework

### Project Structure
```
task-management-api/
├── app/
│   ├── models/         # Database models
│   ├── routes/         # API endpoints
│   ├── middleware/     # Authentication middleware
│   ├── services/       # Business logic
│   └── utils/          # Helper functions
├── config/             # Configuration files
├── tests/              # Test files
├── main.py            # Application entry point
└── requirements.txt   # Project dependencies
```

## 🔧 Setup and Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/task-management-api.git
   cd task-management-api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## 🧪 Running Tests

```bash
pytest tests/
```

## 🌟 Why This Project Matters

This project demonstrates key software engineering skills including:
- RESTful API design principles
- Secure authentication implementation
- Database design and management
- Clean code architecture
- Test-driven development
- API documentation

It's a practical example of how modern backend systems are built and can serve as a foundation for various applications including:
- Todo list apps
- Project management tools
- Team collaboration platforms
- Personal productivity apps

## 📚 API Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login user | No |
| GET | `/api/users/me` | Get current user | Yes |
| POST | `/api/tasks/` | Create task | Yes |
| GET | `/api/tasks/` | List tasks | Yes |
| GET | `/api/tasks/{id}` | Get specific task | Yes |
| PUT | `/api/tasks/{id}` | Update task | Yes |
| DELETE | `/api/tasks/{id}` | Delete task | Yes |

## 🔒 Security Considerations

- All passwords are hashed using bcrypt
- JWT tokens expire after 30 minutes
- Rate limiting prevents brute force attacks
- Input validation prevents SQL injection
- CORS protection for web applications

## 👨‍💻 Author

Connor
