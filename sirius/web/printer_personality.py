import io
import datetime
import flask
from flask.ext import login
import flask_wtf
import wtforms
import base64

from sirius.models.db import db
from sirius.models import hardware
from sirius.models import messages as model_messages
from sirius.protocol import protocol_loop
from sirius.protocol import messages
from sirius.coding import image_encoding
from sirius.coding import templating
from sirius import stats


blueprint = flask.Blueprint('printer_personality', __name__)


class PrintForm(flask_wtf.Form):
    target_printer = wtforms.SelectField(
        'Printer',
        coerce=int,
        validators=[wtforms.validators.DataRequired()],
    )
    face = wtforms.SelectField(
        'Face',
        coerce=unicode,
        validators=[wtforms.validators.DataRequired()],
    )
    message = wtforms.TextAreaField(
        'Message (optional)',
        validators=[],
    )


@login.login_required
@blueprint.route('/printer/<int:printer_id>/personality', methods=['GET', 'POST'])
def printer_personality(printer_id):
    printer = hardware.Printer.query.get(printer_id)
    if printer is None:
        flask.abort(404)

    # PERMISSIONS
    # the printer must belong to this user
    if printer.owner.id == login.current_user.id:
        # fine
        pass
    else:
        flask.abort(404)

    form = PrintForm()
    # Note that the form enforces access permissions: People can't
    # submit a valid printer-id that's not owned by the user
    choices = [
        (x.id, x.name) for x in login.current_user.printers
    ]
    form.target_printer.choices = choices
    form.face.choices = [
        ("default", "Default face"),
        ("happy-long-hair-glasses", "Happy/long hair/glasses face"),
        ("barcode", "Barcode face"),
        ("normal", "\"Normal\" face"),
    ]

    # Set default printer on get
    if flask.request.method != 'POST':
        form.target_printer.data = printer.id
        form.face.data = "default"

    if form.validate_on_submit():
        try:
            printer.change_face(
                from_name=login.current_user.username,
                face=form.face.data,
                message=form.message.data,
            )
            flask.flash('Sent personality to the printer!')
        except hardware.Printer.OfflineError:
            flask.flash(
                "Could not send message because the printer {} is offline.".format(printer.name),
                'error'
            )

        return flask.redirect(flask.url_for(
            'printer_personality.printer_personality',
            printer_id=printer.id))

    return flask.render_template(
        'printer_personality.html',
        printer=printer,
        form=form,
    )
