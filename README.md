# Sweet Shop API

A Django REST API for managing a sweet shop with user authentication, inventory management, and purchase functionality.

## Features

- 🔐 User authentication with JWT tokens
- 🍬 Sweet inventory management
- 🔍 Advanced search and filtering
- 🛒 Purchase functionality with stock management
- 📦 Admin-only restock capabilities
- ✏️ CRUD operations for sweets
- 🧪 Comprehensive test coverage

## Tech Stack

- **Backend**: Django 5.x
- **API Framework**: Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**: SQLite (default) 
- **Testing**: Django Test Framework

## Installation

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/SrinivasSKulal/sweet_api_django
cd sweet_api_django
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install django djangorestframework djangorestframework-simplejwt
```
or 
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create a superuser (admin)**
```bash
python manage.py createsuperuser
```

6. **Run the development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication

#### Register
- **URL**: `/api/auth/register`
- **Method**: `POST`
- **Auth**: Not required
- **Body**:
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```
- **Response**:
```json
{
  "message": "User created Successfully"
}
```

#### Login
- **URL**: `/api/auth/login`
- **Method**: `POST`
- **Auth**: Not required
- **Body**:
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```
- **Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "username": "johndoe"
}
```

### Sweets Management

#### Get All Sweets
- **URL**: `/api/sweets`
- **Method**: `GET`
- **Auth**: Required
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**:
```json
[
  {
    "id": 1,
    "name": "Gulab Jamun",
    "category": "Indian",
    "price": "50.00",
    "quantity": 100
  }
]
```

#### Create Sweet
- **URL**: `/api/sweets`
- **Method**: `POST`
- **Auth**: Required
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**:
```json
{
  "name": "Jalebi",
  "category": "Indian",
  "price": "35.50",
  "quantity": 75
}
```

#### Search Sweets
- **URL**: `/api/sweets/search/`
- **Method**: `GET`
- **Auth**: Required
- **Query Parameters**:
  - `name`: Filter by name (case-insensitive)
  - `category`: Filter by category (case-insensitive)
  - `min_price`: Minimum price
  - `max_price`: Maximum price
- **Example**: `/api/sweets/search/?category=Indian&min_price=40`

#### Update Sweet
- **URL**: `/api/sweets/<id>`
- **Method**: `PUT`
- **Auth**: Required
- **Body**:
```json
{
  "name": "Updated Gulab Jamun",
  "category": "North Indian",
  "price": "55.00",
  "quantity": 120
}
```

#### Delete Sweet
- **URL**: `/api/sweets/<id>`
- **Method**: `DELETE`
- **Auth**: Required (Admin only)
- **Response**: `204 No Content`

### Purchase & Restock

#### Purchase Sweet
- **URL**: `/api/sweets/<id>/purchase`
- **Method**: `POST`
- **Auth**: Required
- **Body**:
```json
{
  "quantity": 10
}
```
- **Response**:
```json
{
  "message": "Purchase complete",
  "purchased_quantity": 10,
  "total_cost": 500.0,
  "sweet": {
    "id": 1,
    "name": "Gulab Jamun",
    "category": "Indian",
    "price": "50.00",
    "quantity": 90
  }
}
```

#### Restock Sweet
- **URL**: `/api/sweets/<id>/restock`
- **Method**: `POST`
- **Auth**: Required (Admin only)
- **Body**:
```json
{
  "quantity": 50
}
```
- **Response**:
```json
{
  "message": "Restock complete",
  "previous_quantity": 90,
  "new_quantity": 140,
  "sweet": { ... }
}
```

## Models

### Sweet
```python
{
  "id": Integer (auto),
  "name": String (max 100 chars),
  "category": String (max 50 chars),
  "price": Decimal (max 10 digits, 2 decimal places),
  "quantity": Integer
}
```

## Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific test class
python manage.py test api.tests.PurchaseTestCase

# Run with verbose output
python manage.py test --verbosity=2

# Run with coverage (install coverage first: pip install coverage)
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Test Coverage

The project includes comprehensive tests for:
- ✅ User authentication (register, login)
- ✅ Sweet CRUD operations
- ✅ Search and filtering
- ✅ Purchase functionality
- ✅ Restock operations
- ✅ Permission checks
- ✅ Error handling

**Total: 36 tests**

## Project Structure

```
sweet_api_django/
├── sweet_model/
│   ├── api/
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── models.py          # Sweet model
│   │   ├── serializer.py      # DRF serializers
│   │   ├── views.py           # API views
│   │   ├── tests.py           # Test cases
│   │   └── urls.py            # URL routing
│   ├── sweet_model/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── manage.py
└── README.md
```

## Frontend Integration

The API can be integrated with any frontend framework. Example using React with Axios:

```javascript
// Login
const response = await axios.post('http://localhost:8000/api/auth/login', {
  username: 'johndoe',
  password: 'SecurePass123!'
});

const token = response.data.access;
localStorage.setItem('access_token', token);

// Fetch sweets
const sweets = await axios.get('http://localhost:8000/api/sweets', {
  headers: {
    Authorization: `Bearer ${token}`
  }
});

// Purchase
await axios.post(
  `http://localhost:8000/api/sweets/${sweetId}/purchase`,
  { quantity: 5 },
  { headers: { Authorization: `Bearer ${token}` } }
);
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful GET/PUT requests
- `201 Created`: Successful POST (creation)
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found

Error response format:
```json
{
  "error": "Error message description"
}
```

## Security Features

- 🔐 JWT-based authentication
- 🔒 Password validation (minimum 8 characters, complexity requirements)
- 🛡️ Admin-only operations (delete, restock)
- 🔄 Atomic database transactions for inventory updates
- ✅ Input validation and sanitization

## Environment Variables

Create a `.env` file for production:

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## Production Deployment

1. Set `DEBUG = False` in settings.py
2. Configure a production database (PostgreSQL recommended)
3. Set up proper `ALLOWED_HOSTS`
4. Use environment variables for sensitive data
5. Collect static files: `python manage.py collectstatic`
6. Use a production WSGI server (Gunicorn, uWSGI)
7. Set up HTTPS with SSL certificates
8. Configure CORS for frontend integration

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Do what you want to do with it no problem

## Contact

Your Name - srinivaskulalwork@gmail.com

Project Link: [https://github.com/SrinivasSKulal/sweet_api_django](https://github.com/yourusername/sweet_api_django)

## Acknowledgments

- Django REST Framework documentation
- Simple JWT documentation
- Django documentation