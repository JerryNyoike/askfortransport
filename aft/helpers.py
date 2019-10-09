import jwt


def verify_token(token, secret):
        ''' whenever a user sends a request accompanied by the jwt
            this function checks its validity by looking at the algorithm used and the expiry time of the token'''
        try:
                return jwt.decode(token, secret, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
                return False
        except jwt.InvalidAlgorithmError:
                return False
