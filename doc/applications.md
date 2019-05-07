# DO NOTE THAT YOU NEED TO ADD THE FINAL / IN THE URLS OR THEY DO NOT WORK AND THAT IS VERY STUPID

**error json:** a json with variable name as keys and a list of errors as values
**URL:** /rooms/(room text id)/applications/
**status:** single character:
- 'p': pending. Default value
- 'a': accepted
- 'r': rejected

## Applications list
Requires being logged in as the room owner.

**expected method:** GET

**Payload:** None

**returns:** a json with a list of application data:
```
"username": (string) the username for the user the application is for
"status": (character) the status of the application
"text_id": (string) a unique text_id used to identify the application.
"updated_at": (string) the date the application was last udpated at. ISO format.
```

## Application creation
Requires being logged in as the room owner.

**expected method:** POST

**Payload:**
```
None
```

**returns:** a json with the created application data:
```
"username": (string) the username for the user the application is for
"status": (character) Will always be 'p' upon creating the application.
"text_id": (string) a unique text_id used to identify the application. Automatically generated upon creation.
"updated_at": (string) the date the application was last udpated at. ISO format.
```

## Application modification
Requires being logged in as the user the application is for.

**expected method:** PATCH

**Payload:** None

**Content:**
```
"text_id": (string) the unique text_id to identify the application
"status": (character) must be 'a', 'p' or 'r'. The new status to update to.
```

**returns:** a json with the created application data:
```
"text_id": (string) the unique text_id used to identify the application. Automatically generated upon creation.
"status": (character) Will always be 'p' upon creating the application.
"username": (string) the username for the user the application is for
"room": (string) the unique text_id used to identify the room the application is for
"updated_at": (string) the date the application was last udpated at. ISO format.
```