import random,os,string,json,requests
from flask_mail import Message
from flask import render_template,url_for,session,request,flash,abort
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash,check_password_hash
from projectapp import app,db
from projectapp.mymodel import Guest, Lga, State, Gift, Transaction, guest_gift,Document,Questions
from projectapp import mail

@app.route('/', methods=['GET','POST'])
def home():
    if request.method=='GET':
        
        try:
        
            response = requests.get('http://127.0.0.1:8030/hostel/api/v1.0/listall/')
            hostels = json.loads(response.text)
        except requests.exceptions.ConnectionError as e:
            hostels=[]
        mystates = db.session.query(State).all()
        return render_template('user/index.html',mystates=mystates, hostels=hostels)
    else:   
        #retrieve form data
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        state = request.form.get('state')
        email = request.form.get('email')
        password = request.form.get('password')
        #save into database
        converted = generate_password_hash(password)
        g = Guest(guest_fname=fname,guest_lname=lname,state_id=state,guest_email=email,guest_pwd=converted)
        db.session.add(g)
        db.session.commit()
        #keep details in session
        session['user'] = g.id
        #save feedback in a flash
        flash('Form has been successfully submitted')
        #redirect to user/profile
        return redirect('user/profile')

@app.route('/user/profile')
def profile():
    loggedin_user = session.get('user')
    if loggedin_user != None:
        data = db.session.query(Guest).get(loggedin_user)
        iv = db.session.query(Document).get(1)
        return render_template('/user/profile.html',data=data,iv=iv)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/user/login', methods=['GET','POST'])
def login():
    if request.method =='GET':
        #1 display a template with login form
        return render_template('user/login.html')
    else:
        #2 retrieve form data
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        #3 write a query to fetch from te guest table where username ='' and password =''
        deets = db.session.query(Guest).filter(Guest.guest_email==username).first()
        #4 if data was fetched, keep the id in session and redirect to profile page
        if deets:
            loggedin_user = deets.id
            hashedpass = deets.pwd
            check = check_password_hash(hashedpass,pwd)
            if check:
                session['user'] = loggedin_user
                return redirect('/user/profile')
            else:
                flash('invalid username or password')
                return redirect(url_for('login'))
        else:
            #5 if data was empty, keep feedback in a flash and redirect to homepage/login page
            flash('invalid username or password')
            return redirect(url_for('login'))

@app.route('/user/gift',methods=['GET','POST'])
def gift():
    loggedin_user = session.get('user')
    if loggedin_user:
        if request.method == 'GET':
            mygifts = db.session.query(Gift).all()
            return render_template('user/gift.html',mygifts=mygifts)
        else:
            #retrieve form data
            selectedgift = request.form.getlist('item')
            if selectedgift:
                for i in selectedgift:
                    totalqty = 'quantity'+str(i)
                    total = request.form.get(totalqty,1)
                    statement = guest_gift.insert().values(gift_id=i, guest_id=loggedin_user,qty=total)
                    db.session.execute(statement)
                db.session.commit()
                flash('Thank you for your donation')
                return redirect('/user/profile')
            else:
                flash('Please select at least one gift item')
                return redirect('/user/gift')
    else:
        return redirect('/login')

    

@app.route('/about-me')
def about():
    pwd = app.config['PASSWORD']
    return render_template('user/about.html',pwd=pwd)


@app.route('/addpicture', methods=['POST','GET'])
def uploadpix():
    if session.get('user') != None:
        if request.method =='GET':
            return render_template()

        else:
            fileobj = request.files['pix']
            original = str(random.random() * 10000000) + fileobj.filename
            destination = 'projectapp/static/images/guest/test.jpg'
            fileobj.save(destination)
            guestid = session.get('user')
            guest = db.session.query(Guest).get(guestid)
            guest.profile_pix = original
            db.session.commit()
            return redirect('/user/profile')
            
    else:
        return redirect('/login')



@app.route('/user/addpicture', methods=['GET','POST'])
def addpicture():
    if session.get('user') != None:
        if request.method=='GET':
            return render_template('user/upload.html')
        else: #form is submitted
            fileobj = request.files['pic']       

            if fileobj.filename == '':
                flash('Please select a file')
                return redirect(url_for('addpicture'))
            else:
                 #get the file extension,  #splits file into 2 parts on the extension
                name, ext = os.path.splitext(fileobj.filename)
                allowed_extensions=['.jpg','.jpeg','.png','.gif']

                if ext not in allowed_extensions:
                    flash(f'Extension {ext}is not allowed')
                    return redirect(url_for('addpicture'))
                else:
                    sample_xters = random.sample(string.ascii_lowercase,10) 
                    newname = ''.join(sample_xters) + ext

                    destination = 'projectapp/static/images/guest/'+newname
                    fileobj.save(destination)
                    ##save the details in the db
                    guestid = session.get('user')
                    guest = db.session.query(Guest).get(guestid)
                    guest.profile_pix=newname
                    db.session.commit() 
                    return redirect('/user/profile')
    else:
        return redirect(url_for('login'))




@app.route('/user/question')
def contact():
    if session.get('user') != None:
        return render_template('quest.html')
    else:
        return redirect(url_for('login'))
     
@app.route('/user/question-ajax')
def questionajax():
    if session.get('user') != None:
        return render_template('quest.html')
    else:
        return redirect(url_for('login'))


@app.route('/user/submitquestion',methods=['POST','GET'])
def submitquestion():
    loggedin = session.get('user')
    if loggedin != None:
        quest = request.form.get('quest')
    
        q = Questions(question=quest,guest_id=loggedin)
        db.session.add(q)
        db.session.commit()
        flash('thank you for asking')
        return redirect(url_for('userprofile'))
    else:
        return redirect(url_for('login'))




@app.route('/user/submitajax',methods=['POST','GET'])
def submitajax():
    loggedin = session.get('user')
    if loggedin != None:
        quest = request.form.get('quest')
        first = request.form.get('fname')
        last = request.form.get('lname')
        csrf_token = request.form.get('csrf_token')
        pixobj = request.files['pix']
        filename = pixobj.filename
        q = Questions(question=quest,guest_id=loggedin)
        db.session.add(q)
        db.session.commit()
        return f"Thank you {first} {last}, Your Questions has been asked, the CSRF TOKEN IS {csrf_token}, and file is {filename}"
    else:
        return "You need to log in to ask a question"




@app.route('/user/availability', methods={"GET","POST"})
def check_availability():
    if request.method == 'GET':
        records = db.session.query(State).all()

        return render_template('user/test.html',record=records)
    else:
        user = request.form.get('user')
        deets = db.session.query(Guest).filter(Guest.guest_email==user).all()
        
        if deets:
            rsp = {"msg":"You have registered with this email", "status":"failed"} 
            return json.dumps(rsp)
        else:
            rsp = {"msg":"Username available", "status":"success"} 
            return json.dumps(rsp)



@app.route('/user/lga')
def lga():
    state = request.args.get('id')
    data = db.session.query(Lga).filter(Lga.state_id==state).all()

    tosend  = "<select class='form-control' name='>" 
    for t in data:
        tosend= tosend + f"<option>{t.lga_name}</option>"
    tosend=tosend+"</select>"

    return tosend


@app.route('/user/donate-cash/',methods=["POST","GET"])
def donate_cash():
    loggedin = session.get('user')
    if loggedin:
        if request.method == 'GET':

            return render_template('user/cashin.html')
        else:
            cash =request.form.get('amt')
            return "Form submitteed here "
    else:
        abort(403)


@app.route('/user/payup')
def paystack():
    loggedin = session.get('user')
    if loggedin:
        return "Transactions completed"
    else:
        abort(403)

def refno():
    sample_xters = random.sample(string.digit,10)
    newname=''.join(sample_xters)
    return newname
@app.route('/user/paycash',methods=["GET","POST"])
def paycash():
    if session.get('user') != None:
        if request.method=="GET":
            return render_template('user/cashins.html')
        else:
            user = session.get('user')
            cashed = request.form.get('amt',0)
            ref=refno()
            session['trxref'] = ref
            inst = Transaction(trx_guestid=user,trx_amt=cashed,trx_status='pending',trx_ref=ref)
            db.session.add(inst)
            db.session.commit()
            return redirect("confirmpay")
    else:
        return redirect(url_for('login'))



@app.route('/user/confirmpay',methods=['GET','POST'])
def confirmpay():
    if session.get('user') !=None and session.get('trxref') !=None:
        ref = session.get('trxref')
        deets = db.session.query(Transaction).filter(Transaction.trx_ref==ref).first()

        if request.method=='GET':
            return render_template('user/confirmpay.html',deets=deets)  
        else:
            #connect to paystack endpoint
            amount = deets.trx_amt * 100
            email=deets.guest.email
            headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_c41b8a36f3b1e4cec6e476893c630d7a171b7d7a"}            
            data = {"reference": ref, "amount": amount, "email": email}
            
            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))

            rsp = json.loads(response.text) 
            if rsp.get('status') == True:
                payurl = rsp['date']['authorization_url']
                return redirect(payurl)
            else:	
                return redirect(url_for('paycash'))
    else:     
        return redirect(url_for('login'))


@app.route('/user/testmail')
def testmail():
    msg = Message("Testing Mail","sender@gmail.com",
    recipients=['abrajoe7@gmail.com'],body='Test Mail')
    fp = open('requirements.txt')
    msg.html = "<div><h1>Welcome user</h1><p>You have successfully logged in clents are waiting for you</p><hr> Signed by Management</div><img src='select the image from the network if necessary'>"
    msg.attach("requirements.txt", "application/txt", fp.read())
    check = mail.send(msg)
    if check:
        return "Mail was sent"
    else:
        return "Checking Mail sending failed...."