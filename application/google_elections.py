import requests
import json
import logging

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


def get_elections(api_key):
    election_api_final = election_api_url.format(api_key)

    resp_elections = requests.get(election_api_final)
    json_elections = resp_elections.json()
    logging.debug("ELECTIONS: " + str(resp_elections.text))

    elections = {}
    for election in json_elections['elections']:
        elections[election['id']] = {'date': election.get('electionDay'),
                                     'name': election.get('name')}

    return elections


def get_elections_wtf(api_key):
    elections = get_elections(api_key)
    election_tuples = []
    for key, value in elections.items():
        election_tuples.append((key, value.get('name')))

    return election_tuples


def get_voterinfo(election, address, api_key):
    voterinfo_api_final = voterinfo_api_url.format(election, api_key)
    ex_dict = {'address': address}
    headers = {'content-type': 'application/json'}

    resp_candidates = requests.post(voterinfo_api_final,
                                    data=json.dumps(ex_dict),
                                    headers=headers)

    json_candidates = resp_candidates.json()
    logging.debug('CANDIDATES: ' + resp_candidates.text)
    return json_candidates


def flatten_voterinfo(election, address, api_key):
    voter_info = get_voterinfo(election, address, api_key)
    logging.debug("VOTER INFO RAW")
    logging.debug(json.dumps(voter_info))
    logging.debug("END VOTER INFO RAW")
    # contest
    #   -candidate
    #       parties
    #           - party 1
    #           - party 2
    #       social media
    #           - sm 1
    #           - sm 2
    contests = voter_info['contests']  # list
    # for each contest
    #   if candidate exists in contest, update candidate to include new party
    #   if candidate does not exist in contest, add candidate
    final_contests = []
    for contest in contests:

        if 'candidates' in contest:  # make sure our contest has candidates
            candidates_list = {}
            for candidate in contest['candidates']:
                if candidate['name'] in candidates_list:
                    candidates_list[candidate['name']]['party'].append(candidate['party'])
                else:
                    # we key off name, for easy lookup
                    candidates_list[candidate['name']] = {}
                    if 'party' in candidate:
                        candidates_list[candidate['name']]['party'] = [candidate['party']]
                    if 'candidateUrl' in candidate:
                        candidates_list[candidate['name']]['candidateUrl'] = candidate['candidateUrl']
                    if 'channels' in candidate:
                        candidates_list[candidate['name']]['channels'] = candidate['channels']

        # final_contests.append({'type': contest['type'],
        #                        'office': contest['office'],
        #                        'level': contest['level'],
        #                        'candidates': candidates_list})
        contest_dict = {}
        for element in ['type', 'office', 'level']:
            if element in contest:
                contest_dict[element] = contest[element]
        contest_dict['candidates'] = candidates_list
        final_contests.append(contest_dict)

    voter_info['contests'] = final_contests
    logging.debug('FLATTEN VOTER INFO')
    logging.debug(json.dumps(voter_info))
    logging.debug('END FLATTEN VOTER INFO')

    return voter_info


def get_representativeinfo(address, api_key):
    representative_api_url_final = representative_api_url.format(address,
                                                                 api_key)
    resp_representatives = requests.get(representative_api_url_final)
    json_respresentatives = resp_representatives.json()
    logging.debug('REPRESENTATIVE INFO: ' + resp_representatives.text)
    return json_respresentatives
