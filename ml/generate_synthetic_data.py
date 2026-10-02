import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_synthetic_data(num_samples=5000):
    np.random.seed(42)
    random.seed(42)
    
    data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    merchant_ids = [f"merch_{i:03d}" for i in range(1, 6)]
    
    for i in range(num_samples):
        # 80% legit, 20% risky
        is_risky = random.random() < 0.2
        
        # Time distribution
        random_days = random.randint(0, 90)
        created_at = start_date + timedelta(days=random_days) + timedelta(minutes=random.randint(0, 1440))
        
        # Base features
        order_value = round(np.random.lognormal(mean=7.0, sigma=1.0), 2)
        items_count = random.randint(1, max(1, int(order_value / 500)))
        merchant_id = random.choice(merchant_ids)
        
        # Risk factors
        address_length = random.randint(50, 100) if not is_risky else random.randint(10, 30)
        phone_valid = 1 if random.random() > 0.05 else (0 if is_risky else 1)
        name_length = random.randint(8, 20) if not is_risky else random.randint(3, 6)
        email_valid = 1 if random.random() > 0.1 else (0 if is_risky else 1)
        
        # History
        past_orders_from_ip = random.randint(0, 2) if not is_risky else random.randint(3, 10)
        
        # Target variable (Failed Delivery / RTO)
        # If risky, 70% chance of failure. If not risky, 5% chance of failure.
        is_rto = 1 if (is_risky and random.random() < 0.7) or (not is_risky and random.random() < 0.05) else 0
        
        data.append({
            'order_id': f"ORD-{created_at.strftime('%Y%m%d')}-{i:06d}",
            'merchant_id': merchant_id,
            'created_at': created_at.isoformat(),
            'order_value': order_value,
            'items_count': items_count,
            'address_length': address_length,
            'phone_valid': phone_valid,
            'name_length': name_length,
            'email_valid': email_valid,
            'past_orders_from_ip': past_orders_from_ip,
            'is_rto': is_rto
        })
        
    df = pd.DataFrame(data)
    
    # Create directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/synthetic_orders.csv', index=False)
    print(f"Generated {len(df)} synthetic orders. Saved to data/synthetic_orders.csv")
    print(df['is_rto'].value_counts(normalize=True))

if __name__ == "__main__":
    generate_synthetic_data()
