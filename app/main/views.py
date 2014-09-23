from flask import render_template, session, redirect, url_for, current_app
from .. import db
from . import main
from .forms import AddressElectionLookup, AddressLookup
from ..google_elections import get_voterinfo, get_representativeinfo


# routing
@main.route('/')
def show_landing_page():
    return render_template('landing_page.html')


@main.route('/voterinfo', methods=['GET', 'POST'])
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
        return redirect(url_for('main.show_elections'))

    return render_template('show_voterinfo.html',
                           voterinfo=session.get('voterinfo'),
                           lookupform=form)


@main.route('/representatives', methods=['GET', 'POST'])
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
