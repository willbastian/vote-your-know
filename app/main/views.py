from flask import render_template, session, redirect, url_for, current_app,\
    flash
from .. import db
from . import main
from .forms import AddressElectionLookup, AddressLookup
from ..google_elections import get_voterinfo, get_representativeinfo,\
    get_elections_wtf


# routing
@main.route('/')
def show_landing_page():
    return render_template('landing_page.html')


@main.route('/voterinfo', methods=['GET', 'POST'])
def show_elections():
    print("show_elections")

    form = AddressElectionLookup()
    # to dynamically build the list, we pass in from the view.
    # see:
    # http://stackoverflow.com/questions/12850605/how-do-i-generate-dynamic-fields-in-wtforms/12854055#12854055
    form.election.choices =\
        get_elections_wtf(current_app.config['ELECTION_API_KEY'])

    if form.validate_on_submit():
        print("form validated voterinfo")
        # TODO use this for display on the form, later
        # can we default form data with quick_form?
        session['address'] = form.address.data
        session['election'] = form.election.data

        return redirect(url_for('main.show_elections'))

    address = session.get('address')
    election = session.get('election')
    voterinfo = {}
    if election is not None and address is not None:
        voterinfo = get_voterinfo(election,
                                  address,
                                  current_app.config['ELECTION_API_KEY'])
        if voterinfo.get("status") != "success":
            flash('Invalid Address or Election entered. Review and try again.')

    return render_template('show_voterinfo.html',
                           voterinfo=voterinfo,
                           lookupform=form)


@main.route('/representatives', methods=['GET', 'POST'])
def show_representatives():
    form = AddressLookup()
    if form.validate_on_submit():
        session['address'] = form.address.data
        return redirect(url_for('main.show_representatives'))

    address = session.get('address')
    representatives = {}
    if address is not None:
        representatives =\
            get_representativeinfo(session.get('address'),
                                   current_app.config['ELECTION_API_KEY'])
    return render_template('show_representativeinfo.html',
                           representatives=representatives,
                           lookupform=form)
