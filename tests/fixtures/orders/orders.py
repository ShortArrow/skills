from repository import OrderRepository


def place_order(customer_id, quantity, repo):
    """Place an order.

    customer_id must not be empty. quantity must be positive.
    Returns the order id, or None if the arguments are invalid or the
    customer does not exist.
    """
    if not customer_id:
        return None
    if quantity <= 0:
        return None
    customer = repo.find_customer(customer_id)
    if customer is None:
        return None
    return repo.save_order(customer_id, quantity)


def checkout(cart, repo):
    if not cart.get("customer_id"):
        return None
    if cart.get("quantity", 0) <= 0:
        return None
    return place_order(cart["customer_id"], cart["quantity"], repo)


def reorder(previous_order_id, repo):
    previous = repo.find_order(previous_order_id)
    if previous is None:
        return None
    if not previous["customer_id"]:
        return None
    if previous["quantity"] <= 0:
        return None
    return place_order(previous["customer_id"], previous["quantity"], repo)
