import pusher
from flask import render_template, jsonify, request, Blueprint
from flaskblog import db
from flask_login import current_user, login_required
from flaskblog.models import Post,Message,User


pusher_client = pusher.Pusher(
  app_id='541187',
  key='1d2e73839f1798803872',
  secret='b375379ac7777b208cff',
  cluster='us2',
  ssl=True
)


main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

@main.route("/message",methods=['POST'])
def message():
    try:

        username = request.form.get('username')
        message = request.form.get('message')
        user = User.query.filter_by(username=username).first()
        new_message = Message(username=username, message=message,image_file=user.image_file)
        image = user.image_file
        print(user.image_fil)
        db.session.add(new_message)
        db.session.commit()
        time = new_message.date_posted.strftime('%B %d %Y - %H:%M:%S')


        pusher_client.trigger('chat-channel', 'new-message', {'username' : username, 'message': message,'time':time,'image':image})

        return jsonify({'result' : 'success'})

    except:

        return jsonify({'result' : 'failure'})




@main.route('/test')
@login_required
def test():
    messages = Message.query.all()
    return render_template('test.html',messages=messages)

@main.route("/about")
def about():
    return render_template('about.html', title='About')
