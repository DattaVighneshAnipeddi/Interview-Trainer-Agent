from app.database.mongodb import users_collection
from app.models.user import create_user
from app.utils.security import hash_password


def register_user(full_name: str, email: str, password: str):
    """
    Register a new user.
    """

    # Check if email already exists
    existing_user = users_collection.find_one({"email": email})

    if existing_user:
        return {
            "success": False,
            "message": "Email already registered."
        }

    # Hash the password
    hashed_password = hash_password(password)

    # Create user document
    user = create_user(
        full_name=full_name,
        email=email,
        password=hashed_password
    )

    # Insert into MongoDB
    users_collection.insert_one(user)

    return {
        "success": True,
        "message": "User registered successfully."
    }
