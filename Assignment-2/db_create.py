from application import db
from application.models import Users,Images

db.create_all()

print("DB created.")
