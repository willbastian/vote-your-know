from flask.ext.wtf import Form
from flask.ext.login import current_user
from wtforms import StringField, SubmitField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required
from ..google_elections import get_elections_wtf
from ..models import SavedElection


# form classes
class AddressElectionLookup(Form):
    """lookup class for the election/address tuple"""

    address = StringField('Address:')
    # caller is responsible for providing choices.
    election = SelectField('Election: ', choices=[])
    saved_searches = QuerySelectField('Saved Searches: ',
                                      query_factory=lambda: SavedElection.query.filter_by(user_id=current_user.get_id()),
                                      get_pk=lambda a: a.id,
                                      get_label=lambda a: a.election_name,
                                      allow_blank=True)
    submit = SubmitField('Submit')

    def validate(self):
        if not Form.validate(self):
            return False
        result = True
        if bool(self.address.data) == bool(self.saved_searches.data):
            result = False
            if not bool(self.address.data):
                self.address.errors.append('Please enter an Address or select a Saved Election')
                self.saved_searches.errors.append('Please enter an Address or select a Saved Election')
            else:
                self.address.errors.append('Only Address or Saved Search may be used. They cannot be used together')
                self.saved_searches.errors.append('Only Address or Saved Search may be used. They cannot be used together')
        return result


class AddressLookup(Form):
    """lookup class for the address only"""
    address = StringField('Address:', validators=[Required()])
    submit = SubmitField('Submit')


class CandidateLookup(Form):
    """lookup class for candidate firstname and lastname"""
    firstname = StringField('First Name:', validators=[Required()])
    lastname = StringField('Last Name:', validators=[Required()])


class SaveElection(Form):
    election_name = StringField('Election Name:', validators=[Required()])
