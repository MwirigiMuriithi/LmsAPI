import random
import string

def generate_token(length=64):
    """Generate a random token."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))
