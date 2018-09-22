import io
import datetime
import flask
from flask.ext import login
from flask import request
import flask_wtf
import wtforms
import base64
import json

from sirius.models.db import db
from sirius.models import hardware
from sirius.models import messages as model_messages
from sirius.protocol import protocol_loop
from sirius.protocol import messages
from sirius.coding import image_encoding
from sirius.coding import templating
from sirius import stats

blueprint = flask.Blueprint('external_api', __name__)

@blueprint.route('/external_api/v1/printer/<int:printer_id>/print_html', methods=['POST'])
@login.login_required
def print_html(printer_id):
    printer = hardware.Printer.query.get(printer_id)
    if printer is None:
        flask.abort(401)

    # PERMISSIONS
    # the printer must either belong to this user, or be
    # owned by a friend
    if printer.owner.id == login.current_user.id:
        # fine
        pass
    elif printer.id in [p.id for p in login.current_user.friends_printers()]:
        # fine
        pass
    else:
        flask.abort(404)

    request.get_data()
    task = json.loads(request.data)
    if not task['message']:
        flask.abort(500)
    if task['print_face'] is not False:
        task['print_face'] = True

    response = {}
    try:
        printer.print_html(
            html=task['message'],
            from_name=login.current_user.username,
            face=task['print_face'],
        )
        response['status'] = 'Sent your message to the printer!'
    except hardware.Printer.OfflineError:
        response['status'] = ("Could not send message because the "
                     "printer {} is offline.").format(printer.name)

    return json.dumps(response)
