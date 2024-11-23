class DPoPBase:
    def __init__(self, ):
        ...

class DPoPProofJWT(DPoPBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def encode_jwt_token(self, headers, payload, key):
        ...

    def decode_jwt_token(self, token, key):
        headers = None
        payload = None
        verify = bool
        ...