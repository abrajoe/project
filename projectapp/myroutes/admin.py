import os,random
from os import name
from flask import render_template,url_for,session,flash,redirect,request
from werkzeug.utils import redirect
from projectapp.mymodel import Document

from projectapp import app,db
from projectapp.mymodel import Gift, Guest,State
from projectapp.forms import InvitationForm


@app.route('/admin/dashboard')
def dashboard(): 
    #get the count of the guests table
    guestnum = db.session.query(Guest).count()
    return render_template('admin/dashboard.html',guestnum=guestnum)

@app.route('/admin/guests')
def allguests(): 
    #get the list of all guests and pass it to the template
    myguests = db.session.query(Guest).all()
    #method1 to get records from both guest table and state table
    data = db.session.query(Guest,State).join(State).all()
    #method2
    #data = Guest.query.join(State).add_columns(State).all()
    return render_template('admin/admin.html',myguests=myguests,data=data)

@app.route('/admin/delete/<int:guestid>')
def delete(guestid): 
    x = db.session.query(Guest).get(guestid)
    db.session.delete(x)
    db.session.commit()
    flash('user deleted')
    return redirect('/admin/guests')

@app.route('/admin', methods=['POST','GET'])
def adminhome(): 
    fen = InvitationForm()
    if request.method == 'GET':
        
        return render_template('admin/admin.html',fen=fen)
    else:
        if fen.validate_on_submit():
            uploaded_file= request.files['ivcard']
            message = request.form.get('message','No Info')
            name, ext = os.path.splitext(uploaded_file.filename)
            newname = str(random.random() * 100000000) + ext
            destination = 'projectapp/static/docs/' +newname
            uploaded_file.save(destination)
            sub = Document(doc_filename=newname,doc_message=message)
            db.session.add(sub)
            db.session.commit()
            flash("I.V successfully uploaded")
            return 'Form will be submitted'


@app.route('/login')
def adminabout(): 
    return render_template('admin/adminpage.html')