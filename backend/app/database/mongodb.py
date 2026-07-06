from pymongo import MongoClient
from app.config import MONGODB_URI, DATABASE_NAME

# Create MongoDB client
client = MongoClient(MONGODB_URI)

# Select database
db = client[DATABASE_NAME]

# Collections
users_collection = db["users"]
resumes_collection = db["resumes"]
interviews_collection = db["interviews"]
results_collection = db["results"]


def test_connection():
    try:
        client.admin.command("ping")
        print("✅ Connected to MongoDB Atlas successfully!")
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")