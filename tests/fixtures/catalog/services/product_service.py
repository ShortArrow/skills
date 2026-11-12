from repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def create_product(self, request):
        if not request.get("actor"):
            raise PermissionError("no actor on request")
        if not request.get("name"):
            raise ValueError("name is required")
        return self.repo.insert({"name": request["name"], "price": request.get("price", 0)})

    def rename_product(self, request):
        if not request.get("actor"):
            raise PermissionError("no actor on request")
        if not request.get("product_id"):
            raise ValueError("product_id is required")
        product = self.repo.find(request["product_id"])
        if product is None:
            return None
        return self.repo.update(request["product_id"], {"name": request["name"]})
