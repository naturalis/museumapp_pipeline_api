# MuseumApp Backend API
*Base URL (tijdelijk): [http://145.136.242.65:5000]*
Voorbeelden in de tekst hieronder gebruiken `localhost`.

## Endpoints
 - `/api/last-updated`: laatste wijzigingsdatum
 - `/api/documents`: documenten
 - `/api/favourites`: lijst met favorieten
 - `/auth`: autorisatie / aanvraag token
 
## last-updated
Het endpoint `/api/last-updated` geeft de meest recente wijzigingsdatum van een van de documenten. Optioneel kan een language-parameter wroden meegegeven die "en" en "nl" herkent. Zonder deze parameter default de service naar "nl":
```bash
curl -X GET http://localhost:5000/api/last-updated?language=en
```
Response
```json
{"last_update_date": "2019-07-25T13:45:36+00:00"}
```

Let op:  `/api/last-updated`  vereist autorisatie (zie onder).

## documents
Via het endpoint `/api/documents` kan een lijst met JSON-documenten worden opgehaald. Optionele parameters zijn "language" (nl,en; default naar "nl") en "key". Met die laatste kan gericht een document worden opgevraagd op basis van de waarde van het document-veld "\_key". Zonder "key" worden alle documenten geretourneerd. Let op, "key" en "language" combineren op dit moment nog niet.
```bash
curl -X GET http://localhost:5000/api/documents
curl -X GET http://localhost:5000/api/documents?language=en
curl -X GET http://localhost:5000/api/documents?key=meles_meles
```
Response (ingekort)
```json
{
  "size": 1206,
  "items": [
    {
      "id": 1,
      "created": "2019-07-25T13:45:36+00:00",
      "last_modified": "2019-07-25T13:45:36+00:00",
      "language": "nl",
      "_key": "meles_meles",
      "favourites_rank": 3,
      "header_image": {
        "url": "http://145.136.242.65:8080/squared_images/RMNH.MAM.60099_1_SQUARED.jpg"
      },
      [...]
    },
    [...]
  ]
}
```
Let op:  `/api/documents`  vereist autorisatie (zie onder).

## favourites
Het endpoint `/api/favourites` geeft een lijst met keys terug van de documenten die een waarde hebben in het veld "favourites_rank". Het endpoint is niet taalafhankelijk.
```bash
curl -X GET http://localhost:5000/api/favourites
```
Response
```json
[
  {
    "favourites_rank": 3,
    "_key": "meles_meles"
  },
  {
    "favourites_rank": 5,
    "_key": "leopardus_tigrinus"
  },
  {
    "favourites_rank": 9,
    "_key": "loxodonta_africana"
  },
  {
    "favourites_rank": 10,
    "_key": "morus_bassanus"
  },
  {
    "favourites_rank": 1,
    "_key": "ursus_maritimus"
  },
  {
    "favourites_rank": 6,
    "_key": "carcharodon_carcharias"
  },
  {
    "favourites_rank": 7,
    "_key": "trichechus_manatus"
  },
  {
    "favourites_rank": 4,
    "_key": "gyps_fulvus"
  },
  {
    "favourites_rank": 8,
    "_key": "eudocimus_ruber"
  }
]

```
Let op:  `/api/favourites`  vereist autorisatie (zie onder).



## Autorisatie
De endpoints vereisen autorisatie door middel van  [JSON Web Tokens](https://jwt.io/). Aanvraag van een token gaat via het endpoint `/auth`:
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
