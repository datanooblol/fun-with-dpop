from cryptography.hazmat.primitives.asymmetric import rsa
from package.keypair_management.utils import create_directory
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from cryptography.hazmat.primitives.serialization import PrivateFormat, PublicFormat, NoEncryption, Encoding

class KPMBase:
    def __init__(self, directory):
        self.directory = directory
        self.private_key_path = 'private_key.pem'
        self.public_key_path = 'public_key.pem'

class KeyPairManagement(KPMBase):
    def __init__(self, directory):
        super().__init__(directory)
        

    def generate_private_and_public_keys(self, )->tuple:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            # you can choose key size as you like, but here is just a suggestion.
            key_size=2048
        )
    # Generate public key
        public_key = private_key.public_key()
        return private_key, public_key
    
    def serialize_keypairs_to_pem(self, private_key, public_key):
        # Serialize private key
        private_key_pem = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=NoEncryption()
        )
        # Serialize public key
        public_key_pem = public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )
        return private_key_pem, public_key_pem

    def save_keypairs_to_pem(self, private_key_pem, public_key_pem)->None:
        directory = self.directory
        create_directory(directory)
        for path, key_pem in zip(
            [self.private_key_path, self.public_key_path],
            [private_key_pem, public_key_pem]
        ):
            filepath = f"{directory}/{path}"
            with open(filepath, "wb") as f:
                f.write(key_pem)

    def __load_key_from_pem(self, name):
        filename = f"{self.directory}/{name}"
        with open(filename, "rb") as f:
            key = f.read()
        return key

    def load_public_key_from_pem(self, convert=False):
        key = self.__load_key_from_pem(name=self.public_key_path)
        if convert==True:
            key = load_pem_public_key(key)
            return key
        return key

    def load_private_key_from_pem(self, convert=False):
        key = self.__load_key_from_pem(name=self.private_key_path)
        if convert==True:
            key = load_pem_private_key(
                key,
                password=None  # If the private key is encrypted, pass the password here
            )
            return key
        return key

    def generate_keypairs(self, ):
        private_key, public_key = self.generate_private_and_public_keys()
        private_key_pem, public_key_pem = self.serialize_keypairs_to_pem(private_key, public_key)
        self.save_keypairs_to_pem(private_key_pem, public_key_pem)