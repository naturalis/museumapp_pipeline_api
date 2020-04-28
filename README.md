# Museumapp Pipeline API


## Endpoints
 - `https://museumapp.naturalis.nl/api/last-updated`: laatste wijzigingsdatum
 - `https://museumapp.naturalis.nl/api/documents`: documenten (één document correspondeert met één soortspagina in de app)
 - `https://museumapp.naturalis.nl/api/favourites`: lijst met favorieten
 - `https://museumapp.naturalis.nl/api/rooms`: lijst van museumzalen plus aantal documenten per zaal
 - `https://museumapp.naturalis.nl/api/name-search`: zoeken op basis van soortnaam en populaire naam
 - `https://museumapp.naturalis.nl/api/key`: ophalen documenten op basis van document key
 - `https://museumapp.naturalis.nl/auth`: autorisatie / aanvraag token
  
## _last-updated_
Het endpoint `/api/last-updated` geeft de meest recente wijzigingsdatum van een van de documenten. Optioneel kan een language-parameter wroden meegegeven die "en" en "nl" herkent. Zonder deze parameter default de service naar "nl". Het endpoint vereist autorisatie (zie onder).
```bash
curl -X GET https://museumapp.naturalis.nl/api/last-updated?language=en
```
Voorbeeldrespons
```json
{"last_update_date": "2019-07-25T13:45:36+00:00"}
```

## _documents_
Via het endpoint `/api/documents` kan een lijst met JSON-documenten worden opgehaald. Optionele parameters zijn "language" (nl,en; default naar "nl") en "key". Met die laatste kan gericht een document worden opgevraagd op basis van de waarde van het document-veld "\_key". Zonder "key" worden alle documenten geretourneerd. Let op, "key" en "language" combineren op dit moment nog niet. Het endpoint vereist autorisatie (zie onder).
```bash
curl -X GET https://museumapp.naturalis.nl/api/documents
curl -X GET https://museumapp.naturalis.nl/api/documents?language=en
curl -X GET https://museumapp.naturalis.nl/api/documents?key=meles_meles
```
Voorbeeldrespons (ingekort)
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

## _favourites_
Het endpoint `/api/favourites` geeft een lijst met keys terug van de documenten die een waarde hebben in het veld "favourites_rank". Het endpoint is niet taalafhankelijk. Het endpoint vereist autorisatie (zie onder).
```bash
curl -X GET https://museumapp.naturalis.nl/api/favourites
```
Voorbeeldrespons
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

## _rooms_
Het endpoint `/api/rooms` geeft een lijst met museumzalen terug, met daarbij het aantal documenten per zaal. Het endpoint is niet taalafhankelijk. Dit endpoint vereist autorisatie (zie onder).
```bash
curl -X GET https://museumapp.naturalis.nl/api/rooms
```
Voorbeeldrespons
```json
{
  "items": [
    {
      "key": "Leven",
      "doc_count": 483
    },
    {
      "key": "De verleiding",
      "doc_count": 465
    },
    {
      "key": "De dood",
      "doc_count": 160
    },
    {
      "key": "De aarde",
      "doc_count": 109
    },
    {
      "key": "LiveScience",
      "doc_count": 108
    },
    {
      "key": "De ijstijd",
      "doc_count": 60
    },
    {
      "key": "Dinotijd",
      "doc_count": 60
    },
    {
      "key": "De vroege mens",
      "doc_count": 12
    }
  ],
  "note": "take note: 'doc_count' is the number of species with an object in the corresponding room, not the actual number of objects"
}

```


## _name-search_
Het endpoint `/api/name-search` maakt zoeken naar documenten op basis van wetenschappelijke of populaire naam mogelijk. De API doet een match van de waarde in `search` op de velden `titles.main` (bevat de wetenschappelijke naam) en `titles.sub` (bevat de populaire naam). `titles.sub` is taalgevoelig (nl of en), maar zoeken gebeurt onafhankelijk van de taal. Let op: _match_ is de daadwerkelijk Elasticsearch match, dus hele delen van de zoektermen moeten matchen met hele delen van de veldwaarden. 'gier' vindt wel 'Vale gier', maar niet 'Monniksgier'. Dit endpoint vereist autorisatie (zie onder).
```bash
curl -X GET https://museumapp.naturalis.nl/api/name-search?search=gier
```

## _key_
Het endpoint `/api/key` haalt documenten op op basis van de `key`. De key van de documenten wordt afgeleid van de wetenschappelijke naam volgens: `Aegypius monachus` => `aegypius_monachus`. Zoeken kan zowel op de letterlijke key, als op wetenschappelijke naam. In dat laatste geval past de API dezelfde transformatie toe op de de zoekterm. `key` is taalonafhankelijk; als er voor een gevraagde key documenten in verschillende talen beschikbaar zijn, worden die allemaal geretourneerd. Dit endpoint vereist autorisatie (zie onder).
```bash
curl -X GET https://museumapp.naturalis.nl/api/key?name=aegypius_monachus
curl -X GET https://museumapp.naturalis.nl/api/key?name=Aegypius%20monachus
```

## Autorisatie
De endpoints vereisen autorisatie door middel van  [JSON Web Tokens](https://jwt.io/). Aanvraag van een token gaat via het endpoint `/auth`:
```bash
curl -H "Content-Type: application/json" -X POST -d '{"username":"arthur","password":"dont_panic"}' https://museumapp.naturalis.nl/auth
```
Voorbeeldrespons:
```bash
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NTkzMTEwNDUsImlhdCI6MTU1OTMxMDc0NSwibmJmIjoxNTU5MzEwNzQ1LCJpZGVudGl0eSI6IjEifQ.BKpjIz-SeHPGXWrTcAbUwNwsOXxC8UMyjnxRFo8iRMA"
}
```
Het token dient vervolgens in alle aanvragen te worden meegezonden als `Authorization`-header. Voorbeeld:
```bash
curl -X GET https://museumapp.naturalis.nl/api/documents -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NTkzMTEwNDUsImlhdCI6MTU1OTMxMDc0NSwibmJmIjoxNTU5MzEwNzQ1LCJpZGVudGl0eSI6IjEifQ.BKpjIz-SeHPGXWrTcAbUwNwsOXxC8UMyjnxRFo8iRMA"
```
Tokens zijn 5 minuten geldig.

