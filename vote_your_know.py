__author__ = 'wbastian'
import sys
import requests
import json
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required

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
voterinfo_api_url = "https://www.googleapis.com/civicinfo/v1/voterinfo/{0}/"\
    "lookup?key={1}"

# This is v2 (updated on 9/19/2014).
# V2 for voterinfo is not yet workign w/o an election.
# 0 = address`
# 1 = api_key
representative_api_url = "https://www.googleapis.com/civicinfo/v2/"\
    "representatives?address={0}&key={1}"

# create our little application :)
print("creating our application....")
app = Flask(__name__)
app.config.from_object(__name__)
print(app.config)
bootstrap = Bootstrap(app)


#############################
# App methods
#############################

# routing
@app.route('/')
def show_landing_page():
    return render_template('landing_page.html')


@app.route('/voterinfo', methods=['GET', 'POST'])
def show_elections():
    print("show_elections")
    form = AddressElectionLookup()
    if form.validate_on_submit():
        print("form validated voterinfo")
        # TODO use this for display on the form, later
        # can we default form data with quick_form?
        session['address'] = form.address.data
        voterinfo = get_voterinfo(form.election.data,
                                  form.address.data)
        session['voterinfo'] = voterinfo
        if voterinfo.get("status") != "success":
            flash('Invalid Address or Election entered. Review and try again.')

        print(session.get('voterinfo'))
        return redirect(url_for('show_elections'))

    return render_template('show_voterinfo.html',
                           voterinfo=session.get('voterinfo'),
                           lookupform=form)


@app.route('/representatives', methods=['GET', 'POST'])
def show_representatives():
    form = AddressLookup()
    representatives = {}
    address = None
    if form.validate_on_submit():
        session['address'] = form.address.data
        representatives = get_representativeinfo(form.address.data)
        session['representatives'] = representatives

    return render_template('show_representativeinfo.html',
                           representatives=session.get('representatives'),
                           lookupform=form)


# support methods
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


# form classes
class AddressElectionLookup(Form):
    """lookup class for the election/address tuple"""
    address = StringField('Address:', validators=[Required()])
    elections = get_elections_wtf()
    election = SelectField('Election: ', choices=elections)
    submit = SubmitField('Submit')


class AddressLookup(Form):
    """lookup class for the address only"""
    address = StringField('Address:', validators=[Required()])
    submit = SubmitField('Submit')

# must go at end!
if __name__ == '__main__':
    print ('starting!')
    app.run(debug=True)
