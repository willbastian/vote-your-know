import requests
import json

# goole api info
api_key = "AIzaSyC6WV29UUFLDn4-kXYcwR9Ucuyz1NpYevY"
# 0 = api_key
election_api_url = "https://www.googleapis.com/civicinfo/v1/elections?key={0}"
# 0 = election
# 1 = api_key
voterinfo_api_url = "https://www.googleapis.com/civicinfo/v1/voterinfo/{0}/"\
    "lookup?key={1}"

# This is v2 (updated on 9/19/2014).
# V2 for voterinfo is not yet workign w/o an election.
# 0 = address`
# 1 = api_key
representative_api_url = "https://www.googleapis.com/civicinfo/v2/"\
    "representatives?address={0}&key={1}"


def get_elections():
    # TODO fix this to cover the WTF functionality
    print("get_elections")
    election_api_final = election_api_url.format(api_key)

    resp_elections = requests.get(election_api_final)
    json_elections = resp_elections.json()

    elections = {}
    for election in json_elections['elections']:
        elections[election['id']] = {'date': election.get('electionDay'),
                                     'name': election.get('name')}
    print("Elections:")
    for key, value in elections.items():
        print(key)

    return elections


def get_elections_wtf():
    elections = get_elections()
    election_tuples = []
    print("ELECTIONS")
    print(elections)
    for key, value in elections.items():
        election_tuples.append((key, value.get('name')))

    print("ELECTION TUPLES")
    print(election_tuples)
    return election_tuples


def get_voterinfo(election, address):
    voterinfo_api_final = voterinfo_api_url.format(election, api_key)
    ex_dict = {'address': address}
    headers = {'content-type': 'application/json'}

    print(voterinfo_api_final)
    print("THIS IS FINAL")
    resp_candidates = requests.post(voterinfo_api_final,
                                    data=json.dumps(ex_dict),
                                    headers=headers)

    json_candidates = resp_candidates.json()
    print(json.dumps(json_candidates))
    return json_candidates


def get_representativeinfo(address):
    representative_api_url_final = representative_api_url.format(address,
                                                                 api_key)
    resp_representatives = requests.get(representative_api_url_final)
    json_respresentatives = resp_representatives.json()

    return json_respresentatives