import requests, json
from dotenv import load_dotenv as loadenv
from os import getenv


def SendRequest(url,method,headers={},json={}):
    res = requests.request(method=method, url=url, json=json, headers=headers)
    if res.status_code != 200:
        print(f"{res.status_code} | {method} | {res.url}\n{res.text}\n")
        return
    print(f"{res.status_code} | {method} | {res.url}\n")
    return json.loads(res.text)

tvSHows = []
f = open("Shows.txt", "r")
tvSHows = f.read()
f.close()
tvSHows = tvSHows.split("\n")
loadenv()
notionT = getenv("notionToken")
dbID = getenv("databaseURL")
dbID = dbID.replace("https://www.notion.so/","")
if len(dbID) > 32:
    dbID = dbID[:32]
pageURL = "https://api.notion.com/v1/pages"
queryURL = ("https://api.notion.com/v1/databases/","/query")
searchURL = "https://api.tvmaze.com/singlesearch/shows?q="
episodesURL = ("https://api.tvmaze.com/shows/","/episodes")
showURL = "https://api.tvmaze.com/shows/"
for show in tvSHows:
    showID = SendRequest(url=searchURL+show,method="GET")["id"]
    episodesData = SendRequest(url=episodesURL[0]+showID+episodesURL[1],method="GET")
    showName = SendRequest(url=showURL+showID,method="GET")["name"]
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
    topEpisodeInDatabase = SendRequest(url=queryURL[0]+dbID+queryURL[1],method="POST", json=query, headers=headers)["results"]
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
            res = SendRequest(method="POST",
                                   url=pageURL
                                ,
                                   json=episode,
                                   headers=headers)
            print(f"{showName} S{str(episode['properties']['Season']['number'])} E{str(episode['properties']['Episode']['number'])}\n")
        else:
            # Find and Update the page
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
            EpisodePageID = SendRequest(method="POST",
                                   url=queryURL[0]+dbID+queryURL[1],
                                   json=query,
                                   headers=headers)["results"][0]["id"]
            # Update Page
            res = SendRequest(method="PATCH",
                                   url=pageURL
                                +EpisodePageID,
                                   json=episode,
                                   headers=headers)
            print(f"{showName} S{str(episode['properties']['Season']['number'])} E{str(episode['properties']['Episode']['number'])}\n"