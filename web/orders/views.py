from rest_framework import generics
from .serializers import OrderCreateSerializer, OrderDetailSerializer
from .tasks import process_order_task
from .models import Order

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    def perform_create(self, serializer):
        order = serializer.save()
        process_order_task.apply_async((order.id,), retry=False)

class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer
