import pusher
from flask import render_template, jsonify,request, Blueprint,redirect
from flaskblog import db
from flask_login import current_user, login_required
from flaskblog.models import Post,Message,User
from datetime import datetime
from pytz import timezone
import pytz
import json
import pprint
import sys
import spotipy
import spotipy.util as util

pusher_client = pusher.Pusher(
  app_id='541241',
  key='d199b9ff7984c46c4f83',
  secret='e0d579e55a6e83dd7397',
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


@main.route("/get-count",methods=['POST'])
def get_count():
    try:
        countdict = pusher_client.channel_info(u'chatchannel', [u"subscription_count"])
        count = countdict['subscription_count']
        pusher_client.trigger('chatchannel', 'update-count', {'count':count})
        return jsonify({'result' : 'success'})
    except:
        print('ERROR')
        return jsonify({'result' : 'failure'})

@main.route("/message",methods=['POST'])
def message():
    try:
        username = request.form.get('username')
        message = request.form.get('message')
        user = User.query.filter_by(username=username).first()
        time = timezone('US/Pacific')
        new_message = Message(username=username, message=message,image_file=user.image_file,date_posted=datetime.now(time))
        image = user.image_file
        db.session.add(new_message)
        db.session.commit()
        time = new_message.date_posted.strftime('%B %d %Y - %H:%M:%S')
        pusher_client.trigger('chatchannel', 'new-message', {'username' : username, 'message': message,'time':time,'image':image})
        return jsonify({'result' : 'success'})

    except:
        print('Error')
        return jsonify({'result' : 'failure'})

@main.route('/test')
@login_required
def test():
    messages = Message.query.all()
    return render_template('test.html',messages=messages)

@main.route("/about")
def about():
    return render_template('about.html', title='About')
