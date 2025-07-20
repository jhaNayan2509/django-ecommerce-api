Django E-commerce REST API
This project is a comprehensive and robust REST API for a small e-commerce system, built with Python, Django, and Django REST Framework. It provides a complete backend solution, featuring a secure authentication system, product catalog management, a full-featured shopping cart, and a transactional order processing workflow.

The API is designed with best practices in mind, including secure handling of credentials, database query optimization, and a clean, logical endpoint structure.

Core Features
User Authentication: Secure JWT-based system for user registration, login, and logout (via refresh token blacklisting).
Profile Management: Authenticated users can view and update their personal profile information.
Product & Category Management: Full CRUD (Create, Read, Update, Delete) API for administrators to manage products and categories.
Public Catalog API: Public, read-only endpoints for browsing products, with support for advanced filtering and pagination.
Advanced Filtering: The product list can be filtered by category name, a range of prices, and stock availability.
Shopping Cart System: A persistent shopping cart for each authenticated user, with functionality to add, view, update quantities, and remove items.
Transactional Order System: A secure, atomic order placement process that converts a cart into a formal order, safely deducts product stock, and maintains data integrity.
Order Management: Users can view their complete order history and have the ability to cancel an order if it is still in a "Pending" state, which correctly restores product stock.
Secure Configuration: Sensitive information like secret keys and database credentials are kept secure using environment variables, following production-ready best practices.
Technology Stack
Backend: Python, Django, Django REST Framework
Database: PostgreSQL
Authentication: djangorestframework-simplejwt (JWT)
Configuration: django-environ
Getting Started: Setup and Installation
Follow these steps to get the project up and running on your local machine.

Prerequisites
You must have Python 3.8+, pip, and PostgreSQL installed and running on your system.

1. Clone the Repository
First, clone this repository to your local machine and navigate into the project directory.

Shell

git clone https://github.com/jhaNayan2509/django-ecommerce-api.git
cd django-ecommerce-api
2. Create and Activate a Virtual Environment
It is highly recommended to use a virtual environment to manage project dependencies.

Shell

# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
3. Configure Environment Variables
This project uses a .env file to manage sensitive credentials. In the project root (the same directory as manage.py), create a file named .env.

Copy the following template into the file and fill it with your own PostgreSQL database credentials.

text

# .env file

# Django Settings
SECRET_KEY='your-strong-and-secret-django-key-here'
DEBUG=True

# Database Credentials
DATABASE_NAME='your_postgres_db_name'
DATABASE_USER='your_postgres_user'
DATABASE_PASSWORD='your_postgres_password'
DATABASE_HOST='localhost'
DATABASE_PORT='5432'
4. Install Dependencies
Install all the required Python packages using the requirements.txt file.

Shell

pip install -r requirements.txt
5. Apply Database Migrations
Apply the database schema to your configured PostgreSQL database.

Shell

python manage.py migrate
6. Create a Superuser (Admin)
An admin account is required to test the admin-only endpoints for managing products and categories.

Shell

python manage.py createsuperuser
Follow the prompts to create your administrator account. Remember the email and password you set.

7. Run the Development Server
You are now ready to run the API server.

Shell

python manage.py runserver
The API will be available at http://127.0.0.1:8000/.

How to Test the API
Here is a guided walkthrough to test the key functionalities of the API using curl. You can also use tools like Postman or Insomnia.

User Authentication Flow
Register a new user:

Shell

curl -X POST http://127.0.0.1:8000/api/users/register/ \
-H "Content-Type: application/json" \
-d '{"email":"testuser@example.com", "password":"SomeSecurePassword123", "name":"Test User", "phone":"1234567890"}'
Log in to get tokens:

Shell

curl -X POST http://127.0.0.1:8000/api/token/ \
-H "Content-Type: application/json" \
-d '{"email":"testuser@example.com", "password":"SomeSecurePassword123"}'
Action: Copy the access and refresh tokens from the response. We will refer to the access token as <ACCESS_TOKEN>.
View your profile (Authenticated Request):

Shell

curl -X GET http://127.0.0.1:8000/api/users/profile/ \
-H "Authorization: Bearer <ACCESS_TOKEN>"
E-commerce Workflow
View public products:

Shell

curl -X GET http://127.0.0.1:8000/api/products/
(Note: This will be empty until an admin adds products.)
Admin: Add a product:

First, get an admin token by logging in with your superuser credentials. Let's call it <ADMIN_TOKEN>.
Create a category, then a product.
Shell

# Create Category
curl -X POST http://127.0.0.1:8000/api/admin/categories/ -H "Authorization: Bearer <ADMIN_TOKEN>" -H "Content-Type: application/json" -d '{"name":"Electronics"}'

# Create Product (assuming category ID 1 was created)
curl -X POST http://127.0.0.1:8000/api/admin/products/ -H "Authorization: Bearer <ADMIN_TOKEN>" -H "Content-Type: application/json" -d '{"name":"Laptop", "description":"A cool laptop", "price":"1299.99", "stock":"10", "category":1}'
User: Add the product to the cart:

Shell

curl -X POST http://127.0.0.1:8000/api/cart/ \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-H "Content-Type: application/json" \
-d '{"product_id":1, "quantity":1}'
User: View the cart:

Shell

curl -X GET http://127.0.0.1:8000/api/cart/ \
-H "Authorization: Bearer <ACCESS_TOKEN>"
User: Place the order:

Shell

curl -X POST http://127.0.0.1:8000/api/orders/create/ \
-H "Authorization: Bearer <ACCESS_TOKEN>"
Action: Note the order id from the response (e.g., 1).
User: View order history:

Shell

curl -X GET http://127.0.0.1:8000/api/orders/ \
-H "Authorization: Bearer <ACCESS_TOKEN>"
User: Cancel the pending order:

Shell

curl -X POST http://127.0.0.1:8000/api/orders/1/cancel/ \
-H "Authorization: Bearer <ACCESS_TOKEN>"
Architectural Notes & Future Enhancements
This project was designed with scalability and performance in mind. The following enhancements are planned as the next steps in its development:

Caching Layer with Redis: To further improve read performance and reduce database load, a caching layer using Redis will be implemented. This will involve caching frequently accessed data, such as the public product list and detail views, with an intelligent invalidation strategy to handle data changes.

Real-Time Notifications with WebSockets: To provide a more interactive user experience, Django Channels will be integrated to deliver real-time notifications. The first planned use case is to notify users instantly via a WebSocket connection when their order status is updated by an administrator (e.g., from "Pending" to "Shipped").