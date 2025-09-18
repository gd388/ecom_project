# Order Processing Scaffold

Contains a minimal Django + Celery + RabbitMQ scaffold for async order processing.

Run with:
1. docker-compose up --build
2. docker-compose exec web python manage.py migrate
3. Create products via admin or shell
4. POST /api/orders/ to create an order

Files included:
- docker-compose.yml
- web/ (Django project + app)
