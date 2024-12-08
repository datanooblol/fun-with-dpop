# fun-with-dpop
This is a repository for learning about OAuth DPop.  
Here are checklist:  

### Server
- key pairs generated by R256 (asymetric crptographic algorithm) 
- code generator
### Client
- key pairs generated by R256 (asymetric crptographic algorithm) 
- code_verifier and code_challenge
# Endpoints
## /authorizer  
The endpoints under this topic are all about authentication and authorization.  
### POST /register
This is where a user registeration taken place.  

Request:  
- headers is not mandatory.
- body must have: username, password.

Response:  
- response message

Error handling:  
- if a user exists, reject with status code `400` and message User '<...>'  already exists
### POST /login
This is where a user logins to the server.  

Request:  
- headers is not mandatory.
- body must have: username, password, [code_challenge](#code_challenge) .

Response:  
- [code](#code)

Error handling:  
- if a user is not exist, reject  with status code `400` and message  User '<...>' not found.  
- if a password is incorrect, reject with status code `400` and message Incorrect password.  
- if more than one users are in the servers, reject with status code `400` and message User <...> duplicated.  

### POST /token  
This is where a user can get access_token and refresh_token after logging in.   

Request:  
- headers: [DPoP](#DPoP)
- body: [grant_type](#grant_type), client_id, [code](#code), [code_verifier](#code_verifier)  

Response:  
- access_token
- refresh_token
- [token_type](#token_type)
- [expires_at](#expires_at)  

Error handling:  
- if DPoP is not exist in headers, reject with status `400` and message DPop missing from request headers.  
- if DPoP.claims.[jti](#jti) is duplicated, reject with status `401` and message Security breach: DPoP replayed.  
- if DPoP.claims.htm is not matched the endpoint's method, reject with status `400` and message http method mismatched.  
- if DPoP.claims.htu is not matched the endpoint, reject with status `400` and message http endpoint mismatched.  
- if DPoP.claims.htm and DPoP.claims.htu are not matched, reject with status `400` and message http method and endpoint mismatched.  
- if DPoP.claims in jti, iat, exp, htm, htu, or client_id, reject with status `400` and message Unexpected error: claim is missing from [DPoP claims](#DPoP_claims).  
- if DPoP.signature cannot be verified, reject with status code `400` and message Unexpected error: Signature verification failed.
- if body.grant_type is not authorization_code, reject with status `400` and message Invalid grant_type. 
- if body.code is missing, reject with status `400` and message code missing.  
- if body.code_verifier is missing, reject with status `400` and message code_virifier missing.  
- if body.client_id is missing, reject with status `400` and message client_id missing. 

### POST /refresh  
This where a user can get a new access_token after the existing one is expired. The user will be redirected here when he or she tries to access `/resource/protected` and got the response status `401` and message `Access token expired.`   

Request:  
- headers: [DPoP](#DPoP)
- body: grant_type, client_id, refresh_token  

Response:  
- access_token
- refresh_token
- [token_type](#token_type)
- [expires_at](#expires_at)  

Error handling:  
- All DPoP.claims' validation is applied the same here.  
- if body.grant_type is not refresh_token, reject with status code `400` and message Invalid grant_type.
- if body.refresh_token is missing, reject with status code `400` and message refresh_token missing.  
- if body.client_id is missing, reject with status code `400` and message client_id missing.  
- if body.client_id is not found in the server, reject with status code `400` and message client_id not found.  
- if refresh_token cannot be verified, reject with status `400` and message Unexpected error: Signature verification failed.  
- if refresh_token is replayed, reject with status code `403` and message Refresh token replayed.  
- if refresh_token is expired, reject with status code `403` and message Unexpected error: refresh token expired. Then update refresh_token and relevant access_token records in the database to active equal to False and remark equal to expired. 

### GET /public-key
This is a public endpoint where everyone can access. The reason is we allow the user to use this public key to encode some messages and send back the server. Later the server will use the private key to decode the message. Another reason is `/resource/others` can access to this endpoint and get public key in order to verify a user's access_token and refresh_token. If the verication is successful, it means the access or refresh token is valid and no one tries to intercept and tamper it. 

Request:  
- headers is not mandatory.  

Response:
- e
- kty
- n

## /resource
Explanation  

### GET /protected
Request:  
- headers: DPoP, [Authorization](#Authorization)  

Response:  
- response access token is valid  

Error handling:  
- All DPoP.claims' validation is applied the same here. 
- if headers.Authorization is missing, reject with status code 400 and message Invalid Headers: Authorization missing.  
- if headers.Authorization's is invalid, reject with status code 400 and message Invalid headers: Authorization invalid format. Try 'DPoP accesstokenwithoutspace'.  
- if headers.Authorization does not start with DPoP, reject with status 400 and message Invalid headers: Authorization invalid bearer. Try 'DPoP' instead of '<...>'. 
- if access_token cannot be verified, reject with status code 400 and message Access token is tampered.  
- if access_token is replayed, reject with status code 401 and message Access token replayed.  
- if access_token is expired, reject with status code 401 and message Access token expired.  

# Glossary: 
- <a id="code_challenge"></a>**code_challenge**: this is a key gerated by a user that will submit at `authorizer/login` stage and server will store it and later use to compare with `code_verifier` in `/authorizer/token`
- <a id="code_verifier"></a>**code_verifier**: a user will submit it to `/authorizer/token` and then encoded. It will be compared to the `code_challenge` submit in `/authorizer/login`. If they are matched, it means this user is valid.  
- <a id="code"></a>**code**: it is generated from the server at `/authorizer/login`. It will store and response back to a user. This code will be later submit to `/authorizer/token` for further validation.  
- <a id="expires_in"></a>**expires_in**: access_token will be expired in n time
- <a id="token_type"></a>**token_type**: value must be `DPoP` 
- <a id="DPoP"></a>**DPoP**: it is short for Demonstrated (Demonstration) Proof of Possession. In this case, we use `DPoP JWT`.
- <a id="Authorization"></a>**Authorization**: Authorization in the headers must use `Authorization: DPoP access_token` only. It's because we follow OAuth DPoP practice.  
- <a id="DPoP_claim"></a>**DPoP claims**: DPoP claims (or body or payload) must contain jti, iat, exp, htm, and htu. Note that client_id here is optional. You can use others to identifiy your user.  
- <a id="signature"></a>**signature**: DPoP signature is signed using DPoP.headers, DPoP.claims and a user's private key.  
- <a id="DPoP_headers"></a>**DPoP headers**: DPoP headers contain typ, alg, jwk. `typ` is a type used dpop+jwt, `alg` is an algorithm for `asymetric key pair cryptography` such as `R256`. `jwk` is a user's public key encoded in this format.

# HTTP Error Definition in this repo
- `400` error with low impact. Try connect again
- `401` error with medium impact. Generally related to access_token, so try /authorizer/refresh for the new tokens
- `403` error with high impact. Generally related to refresh_token, you must go to /authorizer/login to start over