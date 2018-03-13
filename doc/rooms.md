# DO NOTE THAT YOU NEED TO ADD THE FINAL / IN THE URLS OR THEY DO NOT WORK AND THAT IS VERY STUPID

**error json:** a json with variable name as keys and a list of errors as values

## Room list
Can be accessed as a guest.

**expected method:** GET

**Payload:** None

**returns:** a json with a list of room data:
```
"id": room id (integer)
"name": room name (string)
"description": room description (string, may be empty)
"owner": username of the room's creator (string)
"updated_at": last updated (datetime ISO format)
```

## Room Creation
Requires authentication.

**expected method:** POST

**Payload:**
```
"title": room title
"system": game system (dropdown menu from all existing system in the database)
"max_players": maximum players allowed to join
"description": room description (OPTIONAL)
```

**returns:** if successful, a 201 status code
error json otherwise