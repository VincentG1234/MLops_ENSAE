import os
import argparse
import markdown2
import json
import requests

# Set the environment variable to avoid OpenMP runtime conflict
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

OLLAMA_URL = "http://localhost:11434/api/generate"

prompt= """ Vous êtes un assistant qui répond aux questions basées sur le contexte suivant :

appreciate the importance of serve and the second how the surface of a court impacts a certain player’s winning rate.Deliverable 2:
2.1 First denormalization (Surcharge):
Let us look at the query (DA-B).We need to join the tournament table just to retrieve the
kind of surface.Yet, the kind of surface is one of the main distinctions that we can make to
compare tournaments, and that is often relevant when one wants to analyze matches.
----------------------------------------------

main distinctions that we can make to compare tournaments, and that is often relevant when one wants to analyze matches.Indeed, players have different play styles and formations which causes many of them to have
very different results depending on the surface.Therefore, to optimize the query (DA-B), and maybe plenty of other queries of the same
kind, it could be interesting to perform a denormalization by “Surcharge” to add directly to
the match scores table the type of the surface.
----------------------------------------------

interesting to perform a denormalization by “Surcharge” to add directly to the match scores table the type of the surface.This enables a data analyst to avoid making a
join just to retrieve one column.Moreover, integrating the surface type directly into the match scores table is an effective
approach due to the low cardinality of this attribute.Since there are only three possible
values (clay, grass, hard), duplicating this information has a negligible impact on storage.
----------------------------------------------

"T001", "name": "Wimbledon" }, "players": { "winner": "Novak Djokovic", "loser": "Rafael Nadal" }, "stats": { "winner_serve_rating": 85, "loser_serve_rating": 78, ...
}}
We could also embed other statistics which are often interesting in order to avoid making a
join each time.
----------------------------------------------

}} We could also embed other statistics which are often interesting in order to avoid making a join each time.Moreover, once a game is played, its statistics do not change; they are static.Thus, the
denormalization will not imply synchronisation over time, which is optimal.
----------------------------------------------

played, its statistics do not change; they are static.Thus, the denormalization will not imply synchronisation over time, which is optimal.About the cardinality, the relationship between match_scores and match_stats is one-to-one
(1:1), Because of this low-cardinality relationship, embedding is an efficient solution since it
does not lead to excessive data duplication.
----------------------------------------------

With this denormalization, a join will no longer be necessary in the query (DA-A),
accelerating the query.

--------------------------------------------

Historique du chat :
Utilisateur : denormalize. Talk about it.


Question :
denormalize. Talk about it.

Répondez à la question en vous basant uniquement sur le contexte et l'historique fournis.
"""

payload = {
    "model": "tinyllama",
    "prompt": prompt,
    "max_tokens": 200,
}

response = requests.post(OLLAMA_URL, json=payload, stream=True)
print("Answer generated.")

# Initialize an empty string to accumulate the response
full_response = ""

# Process the stream of JSON objects
for line in response.iter_lines():
    if line:
        try:
            json_object = json.loads(line)
            full_response += json_object["response"]
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            print("Line content is not valid JSON:", line)

print("Full response:", full_response)
