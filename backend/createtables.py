from database import engine, Base
from models import FailedPayment, RecoveryAttempt
print("create_tables.py is running")
Base.metadata.create_all(bind=engine)

print("tables created successfully")