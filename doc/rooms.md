# DO NOTE THAT YOU NEED TO ADD THE FINAL / IN THE URLS OR THEY DO NOT WORK AND THAT IS VERY STUPID

**error json:** a json with variable name as keys and a list of errors as values

## Room list
Can be accessed as a guest.

**expected method:** GET

**Payload:** None

**returns:** a json with a list of room data:
```
"id": room id (integer)
"text_id": a generated, easy to remember name for the room (used in URLs)
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
"title": (string) room title
"system": (string) game system name (dropdown menu from all existing system in the database)
"max_players": (integer) maximum players allowed to join
"description": (string) room description (OPTIONAL)
```

**returns:** if successful, a 201 status code, with the data for the new room
error json otherwise

## Room Edition
Requires authentication.


**expected method**: PATCH

**Payload*::
```
"text_id": (string) the generated name for the room.
"name": (string) a new title for the room (OPTIONAL)
"max_players": (string) new maximum number of players allowed (OPTIONAL)
"description": (string) new description for the room (OPTIONAL)
```
Any excess payload or keys that are not in that list are ignored.

**returns**: if successful, 200 status code, with the list of changes (including updated_at, and the room's text_id)
error json otherwise