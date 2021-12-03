import datetime



from projectapp import db

guest_gift = db.Table('guest_gift',db.Column('guest_id',db.Integer, db.ForeignKey('guest.id')),db.Column('gift_id',db.Integer, db.ForeignKey('gift.id')),db.Column('qty',db.Integer()))


class Guest(db.Model):
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    guest_fname = db.Column(db.String(55),nullable=False)
    guest_lname = db.Column(db.String(55),nullable=False)
    guest_email = db.Column(db.String(60),nullable=False)
    profile_pix = db.Column(db.String(100),nullable=True)
    guest_pwd = db.Column(db.String(255),nullable=False)
    date_reg = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    state_id = db.Column(db.Integer(), db.ForeignKey('state.state_id'))
    guest_state = db.relationship('State',backref='myguest')
    guest_gifts = db.relationship('Gift',secondary=guest_gift,backref='myguest')
    questions = db.relationship('Questions',back_populates ='questioner')


class State(db.Model):
    state_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    state_name = db.Column(db.String(55),nullable=False)

class Gift(db.Model):
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    gift_name = db.Column(db.String(55),nullable=False)




class Document(db.Model):
    doc_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    doc_filename= db.Column(db.String(100),nullable=False)
    doc_message= db.Column(db.String(200),nullable=True)
    doc_date=db.Column(db.DateTime(),default=datetime.datetime.utcnow)


class Questions(db.Model):
    q_id= db.Column(db.Integer(), primary_key=True,autoincrement=True)
    guest_id = db.Column(db.Integer(),db.ForeignKey('guest.id'))
    question= db.Column(db.String(255),nullable=True)
    datesent = db.Column(db.DateTime(),default=datetime.datetime.utcnow)
    questioner = db.relationship('Guest',back_populates='questions')


class Lga(db.Model):
    lga_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    state_id = db.Column(db.Integer(),db.ForeignKey('state.state_id'))
    lga_name = db.Column(db.String(55),nullable=False)





class Transaction(db.Model):
    trx_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    trx_guestid = db.Column(db.Integer(),db.ForeignKey('guest.id'), nullable=False)
    trx_amt = db.Column(db.Float(), nullable=False)
    trx_status = db.Column(db.String(40), nullable=False)
    trx_others = db.Column(db.String(255), nullable=True)
    trx_ref= db.Column(db.String(12), nullable=False)
    trx_ipaddress = db.Column(db.String(12), nullable=True)
    trx_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)    

    #set relationship
    guest=db.relationship("Guest",backref="guesttrx")