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
    """ We keep the original Google Voter Info Results intact
    with one key change. The candiates section is now keyed off the candidate
    name, with the value being all releveant candidate informaiton.

    This lets us build out the party to be a list, and to avoid us
    showing multiple candidates under a single election because they happen
    to run under multiple parties.

    Each contest has multiple candidates, and we want to make sure we don't
    repeat names
    """
    voter_info = get_voterinfo(election, address, api_key)
    logging.debug("VOTER INFO RAW")
    logging.debug(json.dumps(voter_info))
    logging.debug("END VOTER INFO RAW")
    contests = voter_info['contests']  # list

    final_contests = []
    final_referendum = []
    for contest in contests:
        if contest['type'].lower() == 'general':
            candidates_list = {}
            for candidate in contest['candidates']:
                if candidate['name'] in candidates_list:
                    candidates_list[candidate['name']]['party'].append(candidate['party'])
                else:
                    # we key off name, for easy lookup
                    candidates_list[candidate['name']] = {}
                    # we aren't ensured to have any of the below.
                    # check for existence first.
                    if 'party' in candidate:
                        candidates_list[candidate['name']]['party'] = [candidate['party']]
                    if 'candidateUrl' in candidate:
                        candidates_list[candidate['name']]['candidateUrl'] = candidate['candidateUrl']
                    if 'channels' in candidate:
                        candidates_list[candidate['name']]['channels'] = candidate['channels']

            contest_dict = {}
            for element in ['type', 'office', 'level']:
                if element in contest:
                    contest_dict[element] = contest[element]
            contest_dict['candidates'] = candidates_list
            final_contests.append(contest_dict)
        elif contest['type'].lower() == 'referendum':
            # we'll add the referendums, as is, to the response in a new section.
            final_referendum.append(contest)

    voter_info['contests'] = final_contests
    voter_info['referendums'] = final_referendum
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
