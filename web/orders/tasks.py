from celery import shared_task, Task
from celery.utils.log import get_task_logger
from django.db import transaction
from django.db.models import F
from django.conf import settings
from .models import Order, Product
import requests
logger = get_task_logger(__name__)

class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    max_retries = 3
    default_retry_delay = 10

@shared_task(bind=True, base=BaseTaskWithRetry, acks_late=True)
def process_order_task(self, order_id):
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order_id)
            if order.status == Order.STATUS_CONFIRMED:
                logger.info("Order %s already confirmed - skipping", order_id)
                return {"status":"already_confirmed"}
            current_task_id = self.request.id
            if order.last_processed_task_id == current_task_id:
                logger.info("Task %s already processed for order %s", current_task_id, order_id)
                return {"status":"already_processed_by_task"}
            order.status = Order.STATUS_PROCESSING
            order.last_processed_task_id = current_task_id
            order.save(update_fields=['status','last_processed_task_id'])
            items = order.items.select_related('product').all()
            product_ids = [it.product_id for it in items]
            products = Product.objects.select_for_update().filter(id__in=product_ids)
            prod_map = {p.id:p for p in products}
            total = 0
            for item in items:
                product = prod_map.get(item.product_id)
                if product is None:
                    raise Exception(f"Product {item.product_id} not found")
                if product.stock < item.quantity:
                    order.status = Order.STATUS_FAILED
                    order.total_amount = 0
                    order.save(update_fields=['status','total_amount'])
                    logger.warning("Insufficient stock for order %s product %s", order_id, product.id)
                    return {"status":"failed_insufficient_stock","product_id":product.id}
                product.stock = F('stock') - item.quantity
                product.save(update_fields=['stock'])
                total += (product.price * item.quantity)
            order.total_amount = total
            order.status = Order.STATUS_CONFIRMED
            order.save(update_fields=['total_amount','status'])
    except Exception as exc:
        logger.exception("Error processing order %s", order_id)
        raise exc
    try:
        if getattr(settings, 'WEBHOOK_URL', None):
            requests.post(settings.WEBHOOK_URL, json={"order_id": order.id, "status": order.status, "total_amount": str(order.total_amount)}, timeout=5)
            order.webhook_sent = True
            order.save(update_fields=['webhook_sent'])
    except Exception as e:
        logger.warning("Webhook failed for order %s: %s", order_id, str(e))
    logger.info("Order %s processed: confirmed total %s", order_id, total)
    return {"status":"confirmed","total":str(total)}
