"""
Payment Processing System - Unified Billing Across All Sub-Companies
Handles subscriptions, one-time payments, and revenue sharing
"""
class PaymentProcessor:
    def __init__(self):
        self.transactions = []
        self.subscriptions = {}
        self.revenue_sharing = {"sentinel": 0.1, "subcompany": 0.9}  # 10% to Sentinel, 90% to sub-company
        
    def process_payment(self, payment_data):
        transaction = {
            "id": f"txn_{len(self.transactions)+1:06d}",
            "customer_id": payment_data.get("customer_id"),
            "company": payment_data.get("company"),
            "amount": payment_data.get("amount"),
            "type": payment_data.get("type", "subscription"),
            "status": "completed",
            "processed_at": datetime.utcnow().isoformat()
        }
        self.transactions.append(transaction)
        
        # Revenue sharing
        company_revenue = transaction["amount"] * self.revenue_sharing["subcompany"]
        sentinel_revenue = transaction["amount"] * self.revenue_sharing["sentinel"]
        
        return {
            "transaction": transaction,
            "revenue_split": {
                "company_gets": company_revenue,
                "sentinel_gets": sentinel_revenue
            }
        }
    
    def create_subscription(self, subscription_data):
        sub_id = f"sub_{len(self.subscriptions)+1:06d}"
        self.subscriptions[sub_id] = {
            "customer_id": subscription_data.get("customer_id"),
            "company": subscription_data.get("company"),
            "plan": subscription_data.get("plan"),
            "amount": subscription_data.get("amount"),
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        return {"subscription_id": sub_id, "status": "active"}
    
    def get_payment_stats(self):
        total_revenue = sum(t["amount"] for t in self.transactions)
        return {
            "total_transactions": len(self.transactions),
            "total_revenue": total_revenue,
            "active_subscriptions": len(self.subscriptions),
            "sentinel_revenue": total_revenue * self.revenue_sharing["sentinel"]
        }

# Global payment processor
payment_processor = PaymentProcessor()
