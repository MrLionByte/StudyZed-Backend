
from mongoengine.errors import NotUniqueError
from .models import User
from mongoengine.queryset import Q

async def get_or_create_user(user_data):
    """
    Fetch the user from the database or create a new one based on user_data.
    """
    
    user_id = user_data.get("user_id", "")
    email = user_data.get("user_email", "")
    role = user_data.get("user_role", "")
    user_code = user_data.get("user_code", "")

    try:
        user = User.objects(user_code=user_code).first()
        if user:
            if user.user_id or user.email:
                User.objects(Q(user_id=user.user_id) | Q(email=user.email)).update(
                    set__email=email,
                    set__user_role=role,
                    set__user_id=user_id
                )
            print(f"Existing user fetched: {user}")
            return user

        user = User(
            user_id=user_id,
            user_code=user_code,
            user_role=role,
            email=email,
        )
        user.save()
        print(f"New user created: {user}")
        return user

    except NotUniqueError as e:
        print(f"Error: User with user_id {user_id} already exists. Details: {e}")
        return None

    except Exception as e:
        print("Unexpected error in user creation:", e)
        return None
