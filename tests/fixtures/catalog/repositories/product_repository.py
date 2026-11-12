class ProductRepository:
    def __init__(self, rows=None):
        self.rows = rows if rows is not None else {}
        self.next_id = 1

    def insert(self, values):
        row_id = self.next_id
        self.next_id += 1
        self.rows[row_id] = dict(values)
        return row_id

    def find(self, row_id):
        return self.rows.get(row_id)

    def update(self, row_id, values):
        if row_id not in self.rows:
            return None
        self.rows[row_id].update(values)
        return row_id
