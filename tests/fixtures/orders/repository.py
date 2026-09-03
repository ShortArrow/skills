from abc import ABC, abstractmethod


class OrderRepository(ABC):
    """The storage interface used by orders.py."""

    @abstractmethod
    def find_customer(self, customer_id):
        ...

    @abstractmethod
    def find_order(self, order_id):
        ...

    @abstractmethod
    def save_order(self, customer_id, quantity):
        ...


class SqliteOrderRepository(OrderRepository):
    def __init__(self, connection):
        self.connection = connection

    def find_customer(self, customer_id):
        row = self.connection.execute(
            "select id from customers where id = ?", (customer_id,)
        ).fetchone()
        return {"id": row[0]} if row else None

    def find_order(self, order_id):
        row = self.connection.execute(
            "select customer_id, quantity from orders where id = ?", (order_id,)
        ).fetchone()
        return {"customer_id": row[0], "quantity": row[1]} if row else None

    def save_order(self, customer_id, quantity):
        cur = self.connection.execute(
            "insert into orders (customer_id, quantity) values (?, ?)",
            (customer_id, quantity),
        )
        return cur.lastrowid
