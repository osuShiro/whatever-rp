# DO NOTE THAT YOU NEED TO ADD THE FINAL / IN THE URLS OR THEY DO NOT WORK AND THAT IS VERY STUPID

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

**returns**: a json containing variable name as key and errors as values

## Login
**URL:** /login/