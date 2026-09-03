from repositories.order_repository import OrderRepository


class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def place_order(self, request):
        if not request.get("actor"):
            raise PermissionError("no actor on request")
        if not request.get("product_id"):
            raise ValueError("product_id is required")
        return self.repo.insert({"product_id": request["product_id"], "quantity": request.get("quantity", 1)})

    def cancel_order(self, request):
        if not request.get("actor"):
            raise PermissionError("no actor on request")
        if not request.get("order_id"):
            raise ValueError("order_id is required")
        order = self.repo.find(request["order_id"])
        if order is None:
            return None
        return self.repo.update(request["order_id"], {"state": "cancelled"})
