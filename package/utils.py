from datetime import timedelta
class Configuration:
    def __init__(self, input_dict: dict):
        for key, value in input_dict.items():
            if isinstance(value, dict):
                # If the value is a dictionary, recursively convert it
                value = Configuration(value)
            setattr(self, key, value)

    def __repr__(self):
        # A helpful string representation for debugging
        return f"{self.__class__.__name__}({self.__dict__})"
    
config = Configuration(input_dict={
    "ACCESS_TOKEN_TIME": int(timedelta(minutes=5).total_seconds()),
    # "ACCESS_TOKEN_TIME": int(timedelta(seconds=1).total_seconds()),
    "REFRESH_TOKEN_TIME": int(timedelta(hours=24).total_seconds()),
    "DPOP_TOKEN_TIME": int(timedelta(seconds=30).total_seconds()),
    "ACCESS_TOKEN_JTI": "access_token_jti",
    "REFRESH_TOKEN_JTI": "refresh_token_jti",
    "DPOP_PROOF_JTI": "dpop_proof_jti",
})