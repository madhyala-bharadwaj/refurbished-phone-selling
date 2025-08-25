# security.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# This is a mock user database. In a real application, this would be stored securely.
fake_users_db = {"admin": {"username": "admin"}}


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    A mock function to "authenticate" a user based on a static token.
    In a real application, this would involve validating the token,
    checking its expiration, and retrieving the user from a database.

    Args:
        token (str): The bearer token from the Authorization header.

    Returns:
        dict: The authenticated user's data.

    Raises:
        HTTPException: If the token is invalid or authentication fails.
    """
    if token != "mock_token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # In a real app, you would decode the token to get the user_id/username
    # and then fetch the user from the database.
    user = fake_users_db.get("admin")
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
