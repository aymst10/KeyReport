# IT Store & Technical Support Django Application

A comprehensive Django web application for managing IT materials store operations and technical support services.

## Features

### Core Store Operations
- **Product Management**: CRUD operations for IT products (cameras, scanners, maps, etc.)
- **Inventory Management**: Stock tracking, low stock alerts
- **Customer Management**: Customer profiles and order history
- **Order Processing**: Shopping cart, checkout, order tracking
- **Category Management**: Product categorization and filtering

### Technical Support
- **Support Tickets**: Create, track, and manage technical support requests
- **Service Requests**: Hardware/software installation, maintenance
- **Document Management**: Invoices, receipts, service reports
- **Customer Portal**: Self-service ticket management

### User Management
- **Authentication**: User registration, login, password reset
- **Authorization**: Role-based access (Admin, Staff, Customer)
- **Profile Management**: User profiles and preferences

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5, Django Templates
- **Authentication**: Django Allauth
- **Forms**: Django Crispy Forms
- **File Handling**: Pillow for image processing

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
it_store/
├── manage.py
├── it_store/          # Main project settings
├── store/             # Store app (products, orders)
├── support/           # Support app (tickets, services)
├── users/             # User management app
├── static/            # Static files (CSS, JS, images)
├── media/             # User uploaded files
└── templates/         # HTML templates
```

## Development Progress

This project demonstrates a junior developer's progression in:
- Django fundamentals and best practices
- Database modeling and relationships
- CRUD operations implementation
- User authentication and authorization
- File handling and document management
- Frontend development with templates
- API design principles
- Testing and debugging skills

## License

MIT License
