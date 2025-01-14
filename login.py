import hashlib

def get_hashed_password(plain_text_password, salt):
    plain_text_password += salt
    return hashlib.sha256(plain_text_password.encode("utf-8")).digest()

def check_password(plain_text_password, hashed_password):
    return get_hashed_password(plain_text_password) == hashed_password


if __name__ == "__main__":
    # password = input("Enter a password: ")
    # hashed_password = get_hashed_password(password)
    # print(f"Hashed password: {hashed_password}")
    # print(f"Check password: {check_password(password, hashed_password)}")
    print(get_hashed_password("password", "proarc").hex("-").upper())