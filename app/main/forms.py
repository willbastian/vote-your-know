from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required
from ..google_elections import get_elections_wtf


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
