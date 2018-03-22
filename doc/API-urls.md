# DO NOTE THAT YOU NEED TO ADD THE FINAL / IN THE URLS OR THEY DO NOT WORK AND THAT IS VERY STUPID

**error json:** a json with variable name as keys and a list of errors as values

## Registration
**URL:** /register/

**expected method:** POST

**Payload**:
```
"username": username
"password1": password
"password2": password confirmation
"email": e-mail address (optional)
```

**returns**: if successful, a json with two keys: "token" with an associated JWT token, and "user", another json with the newly created user's details
an error json otherwise

## Login
**URL:** /login/

**expected method:** POST

**Payload**:
```
"username": username
"password": password
```

**returns**: if successful, a json with a single key "token" and the associated JWT token as value
an error json otherwise

## Logout
**URL:** /logout/

**expected method:** POST

**Payload**: None

**Header:** ```Authorization: JWT jwt_token```

**returns:** if successful, a json with a single key "detail" and value "successfully logged out".
an error json otherwise

## JWT Token Refreshing
**URL**: /refresh-token/

**expected method**: POST

**Payload**:
```
"token": existing JWT token
```

**returns**: if successful, a json with a single key "token" with a new token to use.
An error json otherwise.