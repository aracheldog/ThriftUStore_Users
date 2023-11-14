import google.auth.crypt
import google.auth.jwt
import time


def generate_jwt(
    sa_keyfile,
    sa_email="jwt-182@user-microservice-402518.iam.gserviceaccount.com",
    audience="https://thriftustore-api-2ubvdk157ecvh.apigateway.user-microservice-402518.cloud.goog",
    expiry_length=3600,
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

    # sign with keyfile
    signer = google.auth.crypt.RSASigner.from_service_account_file(sa_keyfile)
    jwt = google.auth.jwt.encode(signer, payload)
    payload = google.auth.jwt.decode(jwt, verify=False)
    print("Bearer {}".format(jwt.decode("utf-8")))
    print()
    print("decoded payload is: ", payload)
    return jwt

if __name__ == '__main__':
    generate_jwt("../user-microservice-apigw.json")
