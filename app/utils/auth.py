from app.db import crud
from passlib.hash import bcrypt
from app.core import get_current_active_user


def authenticate_user(db, email, password):
    user = crud.get_user_by_email(db, email)

    if user is None:
        return None

    if bcrypt.verify(password, user.password):
        return user

    return None
