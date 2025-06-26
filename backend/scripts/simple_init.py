import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import EconomicIndicator
from app.services.bcra_service import generate_demo_data

def simple_init():
    print("Starting database initialization...")
    init_db()
    print("Tables created")
    
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(EconomicIndicator).delete()
        db.commit()
        
        # Add demo data
        demo_data = generate_demo_data()
        for item in demo_data:
            indicator = EconomicIndicator(**item)
            db.add(indicator)
        
        db.commit()
        print(f"Created {len(demo_data)} indicators")
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    simple_init()
