import datetime, random, string
from sirius.models.db import db
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm.attributes import flag_modified

def generate_secret():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))


class PrintKey(db.Model):
    """
    Keys uniquely identify a printer and include a secret so you can print to a
    little printer by just embedding a secret in an URL.
    """
    id = db.Column(db.Integer, primary_key=True)
    secret = db.Column(db.String, default=generate_secret, unique=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    printer_id = db.Column(db.Integer, db.ForeignKey('printer.id'))
    printer = db.relationship('Printer', backref=db.backref('print_keys', lazy='dynamic'))

    number_of_uses = db.Column(db.Integer, default=0, nullable=False)
    senders = db.Column(db.String, default='', nullable=False)

    def record_usage(self, by_name):
        self.number_of_uses += 1
        senders = self.senders.split(',')
        if by_name not in senders:
            senders.append(by_name)
            if senders[0] == '':
                del senders[0]
            self.senders = ','.join(senders)
            flag_modified(self, 'senders')

    parent_id = db.Column(db.Integer, db.ForeignKey('print_key.id'))
    parent = db.relationship(
        'PrintKey',
        backref=db.backref('children', lazy='dynamic'),
        remote_side=[id])

    def senders_formatted(self):
        return ', '.join((s or 'Anonymous') for s in self.senders.split(','))
