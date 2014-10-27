from flask import render_template, session, redirect, url_for, current_app,\
    flash, request
from flask.ext.login import login_required, current_user
from .. import db
from . import main
from .forms import AddressElectionLookup, AddressLookup, CandidateLookup
from ..models import SavedElection, SavedCandidates
from ..google_elections import get_voterinfo, get_representativeinfo,\
    get_elections_wtf, flatten_voterinfo
from ..govtrak import get_bills_voted_on, get_bill
import json
import logging
from nameparser import HumanName
import ast


# routing
@main.route('/')
def show_landing_page():
    return render_template('landing_page.html')


@main.route('/voterinfo', methods=['GET', 'POST'])
def show_elections():
    """builds the voterinfo dictionary to display voting locations and
    candidates in an election

    We use the flatten_voterinfo method in the google_elections helper file
    to ensure we only show a single candidate per office, even if they are
    running under multiple parties
    """
    logging.debug('start show_elections')

    form = AddressElectionLookup()
    # to dynamically build the list, we pass in from the view.
    # see:
    # http://stackoverflow.com/questions/12850605/how-do-i-generate-dynamic-fields-in-wtforms/12854055#12854055
    form.election.choices =\
        get_elections_wtf(current_app.config['ELECTION_API_KEY'])

    if form.validate_on_submit():
        session['address'] = form.address.data
        session['election'] = form.election.data
        if form.saved_searches.data:
            session['saved_search'] = form.saved_searches.data.id
        else:
            session['saved_search'] = None

        return redirect(url_for('main.show_elections'))
    elif form.is_submitted():
        # clear the inputs if we tried to input, and failed.
        session['address'] = None
        session['election'] = None
        session['saved_search'] = None

    address = session.get('address')
    election = session.get('election')
    saved_search = session.get('saved_search')
    form.address.data = address
    form.election.data = election
    if saved_search:
        form.saved_searches.data = SavedElection.query.get(int(saved_search))
    else:
        form.saved_searches.data = None

    if election and address:
        logging.debug('START VOTERINFO')
        voterinfo = flatten_voterinfo(election,
                                      address,
                                      current_app.config['ELECTION_API_KEY'])
        if voterinfo.get("status") != "success":
            flash('Invalid Address or Election entered. Review and try again.')
        logging.debug('END VOTERINFO')
        return render_template('show_voterinfo.html',
                               voterinfo=voterinfo,
                               lookupform=form)
    elif saved_search:
        logging.debug('START SAVED SEARCH')
        election = SavedElection.query.get(int(saved_search))

        candidates = [row.__dict__ for row in election.candidates]
        logging.debug(candidates)
        logging.debug('END SAVED SEARCH')
        return render_template('show_saved_voterinfo.html',
                               voterinfo=candidates,
                               lookupform=form)

    return render_template('show_saved_voterinfo.html',
                           voterinfo={},
                           lookupform=form)


@main.route('/save_voterinfo', methods=['POST'])
@login_required
def save_voterinfo():
    # could have used WTForms to use this
    # and inject the list of candidates into it
    # ...felt like over kill
    selections = request.form.getlist("do_save")

    logging.debug("START NAMES...")
    vote_name = request.form['vote_name']
    existing_election = \
        SavedElection.query.filter_by(election_name=vote_name,
                                      user_id=current_user.id).first()
    if existing_election is None:
        existing_election = SavedElection(election_name=vote_name,
                                          user_id=current_user.id)
        db.session.add(existing_election)

    # existing_election.candidates.delete()
    for selection in selections:
        logging.debug(selection)
        # so dirty. gotta be a better way
        all_info = selection.split('|')
        candidate = all_info[0]
        # Full dict with details
        candidate_detail = ast.literal_eval(all_info[1])
        election = all_info[2]  # e.g. General
        office = all_info[3]  # e.g. Us Congress District 12
        level = all_info[4]  # e.g. federal
        logging.debug(all_info)

        existing_election.candidates.append(
            SavedCandidates(name=candidate,
                            party=', '.join(candidate_detail["party"]),
                            office=office))
    # need to commit here so we can pull the key
    db.session.commit()
    flash('Candiates Successfully Saved as "' + vote_name + '"')

    logging.debug("...END NAMES")
    session['address'] = None
    session['election'] = None
    session['saved_search'] = existing_election.id
    return redirect(url_for('main.show_elections'))


@main.route('/representatives', methods=['GET', 'POST'])
def show_representatives():
    form = AddressLookup()
    if form.validate_on_submit():
        session['address'] = form.address.data
        return redirect(url_for('main.show_representatives'))

    address = session.get('address')
    form.address.data = address
    representatives = {}
    if address:
        representatives =\
            get_representativeinfo(session.get('address'),
                                   current_app.config['ELECTION_API_KEY'])
        for representative in representatives['officials']:
            human_name = HumanName(representative['name'])
            logging.debug(human_name.as_dict())
            representative['first_name'] = human_name.first
            representative['last_name'] = human_name.last
    return render_template('show_representativeinfo.html',
                           representatives=representatives,
                           lookupform=form)


@main.route('/votehistory/<firstname>-<lastname>')
def show_votehistory(firstname, lastname):
    logging.debug('entering show_votehistory')
    form = CandidateLookup()
    votehistory = get_bills_voted_on(firstname, lastname, 10)
    for vote in votehistory:
        full_bill = get_bill(vote['vote']['related_bill'])
        if full_bill is not None:
            vote['full_bill'] = {}
            vote['full_bill']['title'] = full_bill['title']
            vote['full_bill']['link'] = full_bill['link']
    logging.debug('leaving show_votehistory')
    return render_template('show_representative_votehistory.html',
                           votehistory=votehistory,
                           lookupform=form)


@main.route('/votehistory')
def show_votehistory_blank():
    form = CandidateLookup()
    return render_template('show_representative_votehistory.html',
                           votehistory=None,
                           lookupform=form)
