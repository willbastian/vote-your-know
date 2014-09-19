__author__ = 'wbastian'
import sys
import requests
import json
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

# configuration (tbd/in progress)
DATABASE = '/tmp/votr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# goole api info
api_key = "AIzaSyC6WV29UUFLDn4-kXYcwR9Ucuyz1NpYevY"
# 0 = api_key
election_api_url = "https://www.googleapis.com/civicinfo/v1/elections?key={0}"
# 0 = election
# 1 = api_key
voterinfo_api_url = "https://www.googleapis.com/civicinfo/v1/voterinfo/{0}/lookup?key={1}"
# This is v2 (updated on 9/19/2014). V2 for voterinfo is not yet workign w/o an election.
# 0 = address
# 1 = api_key
representative_api_url = "https://www.googleapis.com/civicinfo/v2/representatives?address={0}&key={1}"

print(__name__)
# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def show_landing_page():
    return render_template('landing_page.html')


@app.route('/voterinfo')
def show_elections():
    print("show_elections")
    elections = get_elections()
    return render_template('show_voterinfo.html', elections=elections, voterinfo=None)


@app.route('/voterinfo', methods=['POST'])
def lookup_election():
    elections = get_elections()
    address = request.form['address']
    election = request.form['election']

    # flash('New entry was successfully posted')
    voterinfo = get_voterinfo(election, address)
    print("election:")
    print(election)
    return render_template('show_voterinfo.html', elections=elections,
                           voterinfo=voterinfo)


@app.route('/representatives')
def show_representatives():
    return render_template('show_representativeinfo.html', representatives=None)


@app.route('/representatives', methods=['POST'])
def lookup_representatives():
    address = request.form['address']
    print("Address :" + address)
    representatives = get_representativeinfo(address)
    return render_template('show_representativeinfo.html', representatives=representatives)


def get_elections():
    print("get_elections")
    election_api_final = election_api_url.format(api_key)

    resp_elections = requests.get(election_api_final)
    json_elections = resp_elections.json()

    elections = {}
    for election in json_elections['elections']:
        elections[election['id']] = {'date': election['electionDay'],
                                     'name': election['name']}
    print("Elections:")
    for key, value in elections.items():
        print(key)

    return elections


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

# must go at end!
if __name__ == '__main__':
    print ('starting!')
    app.run(debug=True)

# selection = input('Select Election:')

# voterinfo_api_final = voterinfo_api_url.format(selection, api_key)
# print(voterinfo_api_final)

# address = input('Enter Address (street, city, state, zip):')
