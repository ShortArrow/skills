from services.product_service import ProductService


class ProductController:
    def __init__(self, service: ProductService):
        self.service = service

    def create(self, request):
        return self.service.create_product(request)

    def rename(self, request):
        return self.service.rename_product(request)
