import os
import csv
import time
import requests
import json

SLEEP_SECONDS = 20

def get_users(location):
    users = []

    url = 'https://api.github.com/search/users?q=repos:1 location:{}&per_page=100'.format(location)

    headers = {
        'Accept': 'application/vnd.github.preview'
    }

    page = 0

    while url is not None:
        print 'Getting user for {} page {}'.format(location, page)

        r = requests.get(url, headers=headers)

        j = r.json()

        if 'items' in j:
            [users.append(u) for u in j['items']]

            url = None
            if 'link' in r.headers:
                links = [[b.strip('<> ') for b in x.split(';')] for x in r.headers['link'].split(',')]

                for l in links:
                    if l[1] == 'rel="next"':
                        url = l[0]
                        page += 1
                        break
                else:
                    url = None
        else:
            if r.status_code == 403:
                print 'API limit exceeded, sleeping for {} seconds'.format(SLEEP_SECONDS)
                time.sleep(SLEEP_SECONDS)
            else:
                print r.status_code
                print j


    return users


def get_locations():
    locations = set()

    for prov in ('av', 'bn', 'ce', 'na', 'sa'):
        path = os.path.join('paesi', '{}.csv'.format(prov))

        with open(path) as f:
            reader = csv.reader(f, delimiter=';')

            for row in reader:
                locations.add(row[1])

    return locations


locs = get_locations()

locations = {}

for location in locs:
    locations[location] = get_users(location)


with open('out.json', 'w') as out:
    json.dump(locations, out)
