# Healthcare Backend System

This repository contains a Django-based backend system for a healthcare application. The system provides APIs for user registration, authentication, and managing patient and doctor records.

## Features

- User registration and authentication using JWT
- Patient management (CRUD operations)
- Doctor management (CRUD operations)
- Patient-Doctor mapping functionality
- PostgreSQL database integration
- Secure environment variable configuration

## Tech Stack

- Django 4.2+
- Django REST Framework (DRF)
- PostgreSQL
- JWT Authentication (djangorestframework-simplejwt)

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/healthcare-backend.git
   cd healthcare
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a PostgreSQL database:
   ```sql
   CREATE DATABASE healthcare_db;
   CREATE USER healthcare_user WITH PASSWORD 'securepassword';
   ALTER ROLE healthcare_user SET client_encoding TO 'utf8';
   ALTER ROLE healthcare_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE healthcare_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE healthcare_db TO healthcare_user;
   ```

5. Configure environment variables:
   - Copy the `.env.example` file to `.env`
   - Update the values according to your environment

6. Apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

8. Run the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication APIs
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Log in a user and return a JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Patient Management APIs
- `POST /api/patients/` - Add a new patient (Authenticated users only)
- `GET /api/patients/` - Retrieve all patients created by the authenticated user
- `GET /api/patients/<id>/` - Get details of a specific patient
- `PUT /api/patients/<id>/` - Update patient details
- `DELETE /api/patients/<id>/` - Delete a patient record

### Doctor Management APIs
- `POST /api/doctors/` - Add a new doctor (Authenticated users only)
- `GET /api/doctors/` - Retrieve all doctors
- `GET /api/doctors/<id>/` - Get details of a specific doctor
- `PUT /api/doctors/<id>/` - Update doctor details
- `DELETE /api/doctors/<id>/` - Delete a doctor record

### Patient-Doctor Mapping APIs
- `POST /api/mappings/` - Assign a doctor to a patient
- `GET /api/mappings/` - Retrieve all patient-doctor mappings
- `GET /api/mappings/<patient_id>/` - Get all doctors assigned to a specific patient
- `DELETE /api/mappings/<id>/` - Remove a doctor from a patient

## Testing

To run the tests:
```bash
python manage.py test
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.