# General fields
Unless stated otherwise, all models have the following fields:
### id
Unsigned integer, auto-incremented. Cannot be edited.
#### created_at
Represents the time a model was created. Assigned upon model creation, and untouched afterwards.

**type**: Datetime (UTC format)

**Cannot be edited.**
#### updated_at
Represents the latest update made to the model. Updated every time a change is made to a model.

**type**: Datetime (UTC format)

**default**: created_at date

# GameModel
Represents a game system that players can use.
## Fields
### name
The game system's name.

**type**: string (128 characters max)

**nullable**: no

**can be blank**: no

**default**: None
### dice
What dice system the game uses.
**type**: string (32 characters max)

**nullable**: no

**can be blank**: no

**default**: None

*notes: might be changed for an enum at a later date*

# Room
Represents a game room. For now, the owner is also the GM.
## Fields
### name
The Room's name. Differs from the name given to the room to access it. Filled in by the user.

**type**: string (256 characters max)

**nullable**: no

**can be blank**: no

**default**: ''

### text_id
A string id given to the room to identify and access it. Unique per room.

Automatically generated upon creating a new room.
**type**: string (128 characters max)
**nullable**: no
**can be blank**: no
**default**: ''
### description
A text to describe the room's content. Filled in by the user.

**type**: text

**nullable**: yes

**can be blank**: yes

**default**: ''
### max_players
The maximum number of players allowed to join, room owner excluded.

**type**: integer

**nullable**: no

**can be blank**: no

**default**: 8
### is_private
Determines if the room can be seen without being part of it. Chosen by the user.

**type**: boolean

**nullable**: no

**can be blank**: no

**default**: False
## Foreign Keys
### owner
Owner of the room, and unique GM.

**type**: User

**relation**: Many-to-One

*notes: relation might be changed to One-to-One in a future update.*
### game_model
Which game system is in use by the Room.

**type**: GameModel

**relation**: Many-to-One