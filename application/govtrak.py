import requests
import json
import logging


bill_url = 'https://www.govtrack.us/api/v2/bill'
cosponsorship_url = 'https://www.govtrack.us/api/v2/cosponsorship'
role_url = 'https://www.govtrack.us/api/v2/role'
person_url = 'https://www.govtrack.us/api/v2/person'
person_single_url = person_url + "/{0}"
vote_url = 'https://www.govtrack.us/api/v2/vote'
vote_voter_url = 'https://www.govtrack.us/api/v2/vote_voter'
committee_url = 'https://www.govtrack.us/api/v2/committee'


def get_name_id(firstname, lastname, **kwargs):
    payload = {'lastname': lastname}
    r = requests.get(person_url, params=payload)
    j = r.json()
    people = j.get('objects')
    people = [person
              for person
              in people
              if firstname == '%' or
              person.get('firstname').lower() == firstname.lower()]
    if len(people) == 1:
        return people[0].get('id')
    else:
        # we can either have 0 (no matches)
        # or more than 1 (find correct match on firstname, last name, etc)
        # for now, we just return blank list and will solve it later.
        return None


def get_bills_voted_on(firstname, lastname, fetchlimit=None):
    # todo: unit test -
    # ensure resulting json list has same count as meta.total_count
    # this method is ugly
    nameid = get_name_id(firstname, lastname)
    if nameid:
        # slow, but worth it
        if fetchlimit:
            limit = min(fetchlimit, 5000)
        else:
            limit = 5000

        offset = 0
        payload = {'person': nameid, 'limit': str(limit),
                   'offset': str(offset), 'sort': '-created'}
        r = requests.get(vote_voter_url, params=payload)
        fetched = limit
        j = r.json()
        logging.debug('VOTE VOTER: ' + r.text)
        meta = j.get('meta')
        total_count = None
        voted_bills = []
        if meta:
            total_count = meta.get('total_count')
            voted_bills += j.get('objects')
            while (fetchlimit is None or
                   fetched < fetchlimit) and fetched < total_count:
                offset += limit
                if offset > 10000:
                    # TODO log error
                    offset = 10000

                payload = {'person': nameid, 'limit': str(limit),
                           'offset': str(offset), 'sort': '-created'}
                r = requests.get(vote_voter_url, params=payload)
                fetched += limit
                j = r.json()
                voted_bills += j.get('objects')
        return voted_bills


def get_bill(id):
    if id is not None:
        r = requests.get(bill_url + "/" + str(id))
        j = r.json()
        return j
