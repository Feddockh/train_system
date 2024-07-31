from cryptography.fernet import Fernet

# Function to generate and store a key
def write_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

# Function to load the key
def load_key():
    return open("key.key", "rb").read()

# Generate and write a new key (run once)
write_key()

# Load the previously generated key
key = load_key()
print(key)
cipher_suite = Fernet(key)

# Encrypt a string
plain_text = "Your text to encrypt"
cipher_text = cipher_suite.encrypt(plain_text.encode())
print("Encrypted:", cipher_text)

# Decrypt the string
decrypted_text = cipher_suite.decrypt(cipher_text).decode()
print("Decrypted:", decrypted_text)