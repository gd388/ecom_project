# Order Processing System

This project demonstrates an **asynchronous order processing system** using **Django + PostgreSQL + RabbitMQ + Celery**, with support for webhooks and monitoring.

---

## 1️⃣ Setup Instructions

### Prerequisites

* Docker & Docker Compose installed
* Optional: Postman or curl for testing API

### Steps

1. **Move to the project directory**

```bash
cd order_project
```

2. **Copy environment file**

```bash
cp web/.env.example web/.env
```

* Update `.env` if you want custom credentials.

3. **Build and start services**

```bash
docker-compose up --build
```

* Services started:

  * `web` → Django API
  * `db` → PostgreSQL
  * `rabbitmq` → Message broker with management UI
  * `worker` → Celery worker
  * `flower` → Celery monitoring UI

4. **Apply database migrations**

```bash
docker-compose exec web python manage.py migrate
```

5. **Create a superuser (optional)**

```bash
docker-compose exec web python manage.py createsuperuser
```

6. **Seed products (optional)**

```bash
docker-compose exec web python manage.py shell
```

Inside Django shell:

```python
from orders.models import Product
Product.objects.create(name="Laptop", stock=10, price=55000)
Product.objects.create(name="Mouse", stock=50, price=500)
exit()
```

---

## 2️⃣ API Usage

### Create Order

**POST** `/api/orders/`
**Request body:**

```json
{
  "items": [
    {"product_id": 1, "quantity": 2},
    {"product_id": 2, "quantity": 1}
  ]
}
```

**Response:**

```json
{
  "id": 1,
  "status": "pending",
  "items": [
    {"id": 1, "product": "Laptop", "quantity": 2},
    {"id": 2, "product": "Mouse", "quantity": 1}
  ]
}
```

* Celery processes the order asynchronously.
* Order status changes from `pending` → `processing` → `confirmed` or `failed`.

### Get Order Details

**GET** `/api/orders/<order_id>/`
**Response:**

```json
{
  "id": 1,
  "status": "confirmed",
  "total_amount": "1100.00",
  "items": [
    {"id": 1, "product": "Laptop", "quantity": 2},
    {"id": 2, "product": "Mouse", "quantity": 1}
  ],
  "webhook_sent": true
}
```

### Admin Panel

* URL: `/admin/`
* Manage `Product`, `Order`, and `OrderItem`
* Create or update products easily.

### Celery & RabbitMQ Monitoring

* **Flower UI:** [http://localhost:5555](http://localhost:5555)
* **RabbitMQ Management UI:** [http://localhost:15672](http://localhost:15672)

  * Default credentials: `guest / guest`

---

## 3️⃣ Design Notes

### Architecture

* **Django API** → Accepts orders, stores in PostgreSQL.
* **Celery Worker + RabbitMQ** → Processes orders asynchronously.
* **Tasks**:

  * Verify stock
  * Deduct inventory
  * Calculate total
  * Update order status
  * Send webhook (if configured)
* **Celery Beat** (optional) → Schedule recurring tasks like daily sales summary.
* **Idempotency** → Task ensures each order is processed only once.
* **Atomic Transactions** → Prevents partial updates (order + stock).

### Models

* **Product**: Stores stock and price.
* **Order**: Tracks status, total amount, webhook sent flag, and last processed task ID.
* **OrderItem**: Stores product and quantity for each order.

### Features

* Async order processing
* Idempotent Celery tasks
* Atomic DB transactions
* Webhook support with tracking (`webhook_sent`)
* Monitoring via Flower & RabbitMQ UI
* Dockerized setup for easy deployment


