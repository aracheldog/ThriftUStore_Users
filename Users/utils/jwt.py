import google.auth.crypt
import google.auth.jwt
import time


# the audience is the api gw client id
def generate_jwt(
    sa_keyfile= '../user-microservice-apigw.json',
    sa_email="jwt-182@user-microservice-402518.iam.gserviceaccount.com",
    audience="https://thriftustore-api-2ubvdk157ecvh.apigateway.user-microservice-402518.cloud.goog",
    expiry_length=36000,
    personalized_claims=None,
):

    """Generates a signed JSON Web Token using a Google API Service Account."""
    now = int(time.time())

    # build payload
    payload = {
        "iat": now,
        # expires after 'expiry_length' seconds.
        "exp": now + expiry_length,
        # iss must match 'issuer' in the security configuration in your
        # swagger spec (e.g. service account email). It can be any string.
        "iss": sa_email,
        "aud": audience,
        # sub and email should match the service account's email address
        "sub": sa_email,
        "email": sa_email,
    }

    # Add personalized claims to the payload
    if personalized_claims:
        payload.update(personalized_claims)

    # sign with keyfile
    signer = google.auth.crypt.RSASigner.from_service_account_file(sa_keyfile)
    jwt = google.auth.jwt.encode(signer, payload).decode("utf-8")
    payload = google.auth.jwt.decode(jwt, verify=False)
    print(jwt)
    print()
    print("decoded payload is: ", payload)
    return jwt

# Example usage with personalized claims
# personalized_claims = {
#     "user_email": "123",
# }

if __name__ == '__main__':
    generate_jwt("../user-microservice-apigw.json")
