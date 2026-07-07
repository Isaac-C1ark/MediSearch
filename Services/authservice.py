def authenticate(email, password):

    fake_users = {
        "padu": {
            "password": "1234",
            "role": "user"
        },
        "hagu": {
            "password": "1234",
            "role": "seller"
        }
    }

    user = fake_users.get(email)

    if user and user["password"] == password:
        return {
            "success": True,
            "role": user["role"]
        }

    return {
        "success": False,
        "role": None
    }