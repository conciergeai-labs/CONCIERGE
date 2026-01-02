import uuid
import random

def generate_payment_link(amount):
    """
    Simulates creating a payment link with a real provider.
    Returns: (Fake URL, Unique Transaction ID)
    """
    # 1. Create a unique ID for this transaction
    payment_id = f"PAY-{str(uuid.uuid4())[:8].upper()}"
    
    # 2. Generate a fake URL that looks real
    # In a real app, this would be: razorpay.com/pay/{payment_id}
    payment_url = f"https://secure-pay.mockbank.com/{payment_id}?amt={amount}"
    
    return payment_url, payment_id