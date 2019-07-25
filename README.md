# MuseumApp Backend API
*Base URL (tijdelijk): [http://145.136.242.65:5000]*
Voorbeelden in de tekst hieronder gebruiken `localhost`.

## Endpoints
 - `/api/last-updated`: laatste wijzigingsdatum
 - `/api/documents`: documenten
 - `/api/favourites`: lijst met favorieten
 - `/auth`: autorisatie / aanvraag token
 
## last-updated
Het endpoint `/api/last-updated` geeft de meest recente wijzigingsdatum
```bash
curl -X GET http://localhost:5000/api/ids 
```
Response
```json
{
    "size": 4,
    "items": [
        {
            "created": "2019-01-01 12:34:56",
            "id": 1
        },
        {
            "created": "2019-03-01 12:34:56",
            "id": 3
        },
        {
            "created": "2019-02-01 12:34:56",
            "id": 2
        },
        {
            "created": "2019-04-01 12:34:56",
            "id": 4
        }
    ]
}
```
Door middel van de parameter `from` kan de response worden beperkt tot documenten die zijn aangemaakt (= nieuw of sindsdien gewijzigd) na een bepaalde datum/tijd. Format is: `'%Y-%m-%dT%H:%M:%S`:
```bash
curl -X GET http://localhost:5000/api/ids?from=2019-03-01T23:23:23
```
Let op:  `/api/ids`  vereist autorisatie (zie onder).

## Documenten
Via het endpoint `/api/documents` kan een lijst met JSON-documenten worden opgehaald. Zonder parameter worden alle beschikbare ID's teruggegeven:
```bash
curl -X GET http://localhost:5000/api/documents 
```
Door middel van de parameter `from` kan de response worden beperkt tot documenten die zijn aangemaakt (= nieuw of sindsdien gewijzigd) na een bepaalde datum/tijd. Format is: `'%Y-%m-%dT%H:%M:%S`:
```bash
curl -X GET http://localhost:5000/api/documents?from=2019-03-01T23:23:23
```
Door middel van de parameter `id` kan een specifiek document worden opgevraagd:
```bash
curl -X GET http://localhost:5000/api/documents?id=2
```
Let op:  `/api/documents`  vereist autorisatie (zie onder).



## Autorisatie
De endpoints `/api/ids` en `/api/documents` vereisen autorisatie door middel van  [JSON Web Tokens](https://jwt.io/). Aanvraag van een token gaat via het endpoint `/auth`:
```bash
curl -H "Content-Type: application/json" -X POST -d '{"username":"arthur","password":"dont_panic"}' http://localhost:5000/auth
```
Response:
```bash
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NTkzMTEwNDUsImlhdCI6MTU1OTMxMDc0NSwibmJmIjoxNTU5MzEwNzQ1LCJpZGVudGl0eSI6IjEifQ.BKpjIz-SeHPGXWrTcAbUwNwsOXxC8UMyjnxRFo8iRMA"
}
```
Het token dient vervolgens in alle aanvragen te worden meegezonden als `Authorization`-header. Voorbeeld:
```bash
curl -X GET http://localhost:5000/api/ids -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NTkzMTEwNDUsImlhdCI6MTU1OTMxMDc0NSwibmJmIjoxNTU5MzEwNzQ1LCJpZGVudGl0eSI6IjEifQ.BKpjIz-SeHPGXWrTcAbUwNwsOXxC8UMyjnxRFo8iRMA"
```
Tokens zijn 5 minuten geldig.

## Errors
