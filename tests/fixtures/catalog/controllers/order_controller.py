from services.order_service import OrderService


class OrderController:
    def __init__(self, service: OrderService):
        self.service = service

    def place(self, request):
        return self.service.place_order(request)

    def cancel(self, request):
        return self.service.cancel_order(request)
