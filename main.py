import requests, json
from os import getenv

tvSHows = []
f = open("Shows.txt", "r")
tvSHows = f.read()
f.close()
tvSHows = tvSHows.split("\n")
notionT = getenv("notionTokeTest")
dbID = getenv("databaseID")
newPageURL = "https://api.notion.com/v1/pages"
queryURL = f"https://api.notion.com/v1/databases/{dbID}/query"
for show in tvSHows:
    #Retrive the show Data
    searchURL = f"https://api.tvmaze.com/singlesearch/shows?q={show}"
    method = "GET"
    res = requests.request(method, url=searchURL)
    if res.status_code == 200:
        print(f"{res.status_code} | {method} | {res.url}\n")
    else:
        print(f"{res.status_code} | {method} | {res.url}\n{res.text}\n")
        quit()
    showID = (json.loads(res.text))["id"]
    episodesURL = f"https://api.tvmaze.com/shows/{showID}/episodes"
    showURL = f"https://api.tvmaze.com/shows/{showID}"
    res = requests.request(method, url=episodesURL)
    if res.status_code == 200:
        print(f"{res.status_code} | {method} | {res.url}\n")
    else:
        print(f"{res.status_code} | {method} | {res.url}\n{res.text}\n")
        quit()
    episodesData = (json.loads(res.text))
    res = requests.request(method, url=showURL)
    if res.status_code == 200:
        print(f"{res.status_code} | {method} | {res.url}\n")
    else:
        print(f"{res.status_code} | {method} | {res.url}\n{res.text}\n")
        quit()
    showName = (json.loads(res.text))["name"]
    headers = {
        "Authorization": f"Bearer {notionT}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    method = "POST"
    # Check if its already in the database
    query = {
        "page_size":
        1,
        "filter": {
            "property": "TV Show",
            "rich_text": {
                "equals": showName
            }
        },
        "sorts": [{
            "property": "Season",
            "direction": "descending"
        }, {
            "property": "Episode",
            "direction": "descending"
        }]
    }
    res = requests.request(method=method,
                           url=queryURL,
                           json=query,
                           headers=headers)
    if res.status_code == 200:
        print(f"{res.status_code} | {method} | {res.url}\n")
    else:
        print(f"{res.status_code} | {method} | {res.url}\n{res.text}\n")
        quit()
    topEpisodeInDatabase = (json.loads(res.text))["results"]
    if len(topEpisodeInDatabase
           ) == 0:  ## Check what is returned if it doesnt exist
        topEpisodeInDatabase = {
            "properties": {
                "Season": {
                    "number": 0
                },
                "Episode": {
                    "number": 0
                },
                'Location': {
                    'rich_text': []
                }
            }
        }
    else:
        topEpisodeInDatabase = topEpisodeInDatabase[0]
    episodeNotionData = []
    for episode in episodesData:
        # Parse the data into a format notion can understand
        episodeNotionData.append({
            "parent": {
                "database_id": dbID
            },
            "properties": {
                'Location': {
                    'rich_text':
                    topEpisodeInDatabase["properties"]["Location"]["rich_text"]
                },
                'Episode': {
                    'number': episode["number"]
                },
                'Season': {
                    'number': episode["season"]
                },
                'Runtime': {
                    'number': episode["runtime"]
                },
                'Type': {
                    'select': {
                        'id': '8aea8181-07b7-4c7d-8dc6-3e441eb917a7',
                        'name': 'TV',
                        'color': 'green'
                    }
                },
                'TV Show': {
                    'rich_text': [{
                        'text': {
                            'content': showName
                        }
                    }]
                },
                'Episode Name': {
                    'title': [{
                        'text': {
                            'content': episode["name"]
                        }
                    }]
                }
            }
        })
        if len(episode["airdate"]) >= 9:
            episodeNotionData[len(episodeNotionData) - 1]["properties"].update(
                {"Released": {
                    "date": {
                        "start": episode["airdate"]
                    }
                }})
    for episode in episodeNotionData:
        if ((topEpisodeInDatabase["properties"]["Season"]["number"]
             == episode["properties"]["Season"]["number"]) and
            (topEpisodeInDatabase["properties"]["Episode"]["number"] <
             episode["properties"]["Episode"]["number"])) or (
                 topEpisodeInDatabase["properties"]["Season"]["number"] <
                 episode["properties"]["Season"]["number"]):
            method = "POST"
            res = requests.request(method=method,
                                   url=newPageURL,
                                   json=episode,
                                   headers=headers)
            if res.status_code == 200:
                print(
                    f"{res.status_code} | {method} | {showName} S{str(episode['properties']['Season']['number'])} E{str(episode['properties']['Episode']['number'])}\n"
                )
            else:
                print(
                    f"{res.status_code} | {method} | {res.url}\n{res.text}\n")
                quit()

        else:
            # Find and Update the page
            method = "POST"
            query = {
                "page_size":
                1,
                "filter": {
                    "and": [{
                        "property": "TV Show",
                        "rich_text": {
                            "equals": showName
                        }
                    }, {
                        "property": "Episode",
                        "number": {
                            "equals":
                            episode["properties"]["Episode"]["number"]
                        }
                    }, {
                        "property": "Season",
                        "number": {
                            "equals": episode["properties"]["Season"]["number"]
                        }
                    }]
                },
                "sorts": [{
                    "property": "Season",
                    "direction": "descending"
                }, {
                    "property": "Episode",
                    "direction": "descending"
                }]
            }
            res = requests.request(method=method,
                                   url=queryURL,
                                   json=query,
                                   headers=headers)
            if res.status_code == 200:
                print(f"{res.status_code} | {method} | {res.url}\n")
            else:
                print(
                    f"{res.status_code} | {method} | {res.url}\n{res.text}\n")
                quit()
            EpisodePageID = (json.loads(res.text))["results"][0]["id"]
            # Update Page
            method = "PATCH"
            updateURL = f"https://api.notion.com/v1/pages/{EpisodePageID}"
            res = requests.request(method=method,
                                   url=updateURL,
                                   json=episode,
                                   headers=headers)
            if res.status_code == 200:
                print(
                    f"{res.status_code} | {method} | {showName} S{str(episode['properties']['Season']['number'])} E{str(episode['properties']['Episode']['number'])}\n"
                )
            else:
                print(
                    f"{res.status_code} | {method} | {res.url}\n{res.text}\n")
                quit()
