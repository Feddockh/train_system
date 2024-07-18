from cryptography.fernet import Fernet

# Generate a key
key = Fernet.generate_key()
print(f"Generated Key: {key.decode()}")

# Initialize the Fernet cipher suite with the generated key
cipher_suite = Fernet(key)

# Function to encrypt data
def encrypt(data: str) -> bytes:
    # Encode the data to bytes and encrypt
    encrypted_data = cipher_suite.encrypt(data.encode('utf-8'))
    return encrypted_data

# Function to decrypt data
def decrypt(encrypted_data: bytes) -> str:
    # Decrypt the data and decode to string
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode('utf-8')
    return decrypted_data

# Example data to encrypt
data = {"Train1" : 50, "Train2" : 200}
data_str = str(data)

# Encrypt the data
encrypted_data = encrypt(data_str)
print(f"Encrypted Data: {encrypted_data}")

# Decrypt the data
decrypted_data = decrypt(encrypted_data)
print(f"Decrypted Data: {decrypted_data}")