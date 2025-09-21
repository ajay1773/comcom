from app.services.db.db import db_service, Order

class OrderService:
    def __init__(self):
        self.db_service = db_service

    async def create_order(self, order: Order):
        await self.db_service.create_order(order)

order_service = OrderService()
