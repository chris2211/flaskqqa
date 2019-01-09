#encoding: utf-8

from flask import Flask,render_template,request,url_for,redirect,session,g
import config
from models import User,Question,Answer
from exts import db
from functools import wraps
from sqlalchemy import or_


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)



def login_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if session.get('user_id'):
            return func(*args,**kwargs)
        else:
            return redirect(url_for('login'))

    return wrapper


@app.route('/')
def index():
    context = {
        'questions' : Question.query.order_by('-create_time').all()
    }
    return render_template('index.html')


@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return u'mobile or password error'

@app.route('/detail/<question_id>',methods=['GET','POST'])
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    return render_template('detail.html',question=question_model)


@app.route('/add_answer/',methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('answer_content')
    question_id = request.form.get('question_id')

    answer = Answer(content=content)
    #user_id = session['user_id']
    #user = User.query.filter(User.id == user_id).first()
    answer.author = g.user
    question = Question.query.filter(Question.id == question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail',question_id=question_id))


@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if hasattr(g,'user'):
        return {'user': g.user}
    return {}


@app.before_request
def my_before_request():
    user_id = session.get("user_id")
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user = user



@app.route('/logout/')
def logout():
    #session.pop('user_id')
    #del session['user_id']
    session.clear()
    return redirect(url_for('login'))


@app.route('/question',methods=['GET','POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        Question(title=title,content=content)
        #user_id = session.get('user_id')
        #user = User.query.filter(User.id == user_id).first()
        question.author = g.user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/regist/',methods=['GET','POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return u'this phone num already registed'
        else:
            if password1 != password2:
                return u'password not fit'
            else:
                user = User(telephone=telephone,username = username,password = password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))


@app.route('/search/')
def search():
    q = request.args.get('q')
    questions = Question.query.filter(or_(Question.title.contains(q),Question.content.contains(q))).order_by('-create_time')
    return render_template('index.html',questions=questions)

if __name__ == '__main__':
    app.run()

