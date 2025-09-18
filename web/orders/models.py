from django.db import models
class Product(models.Model):
    name = models.CharField(max_length=255)
    stock = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self): return self.name

class Order(models.Model):
    STATUS_PENDING='pending'
    STATUS_CONFIRMED='confirmed'
    STATUS_FAILED='failed'
    STATUS_PROCESSING='processing'
    STATUS_CHOICES=[(STATUS_PENDING,'Pending'),(STATUS_PROCESSING,'Processing'),
                    (STATUS_CONFIRMED,'Confirmed'),(STATUS_FAILED,'Failed')]
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    last_processed_task_id = models.CharField(max_length=255, null=True, blank=True)
    webhook_sent = models.BooleanField(default=False)
    def __str__(self): return f"Order {self.pk} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
