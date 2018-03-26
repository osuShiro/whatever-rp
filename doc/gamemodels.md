# DO NOTE THAT YOU NEED TO ADD THE FINAL / IN THE URLS OR THEY DO NOT WORK AND THAT IS VERY STUPID

**error json:** a json with variable name as keys and a list of errors as values

## GameModel list

**expected method**: GET

**Payload**: None

**returns**: a json with a list of gamemodel data:
```
"name": (string) game model name
"dice": (string) dice system used
"updated_at" (string) last updated (datetime ISO format)
```