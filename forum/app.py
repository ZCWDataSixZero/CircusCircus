
from flask import render_template, request
from flask_login import LoginManager
from forum.models import Subforum, db, User
from flask_socketio import SocketIO, join_room, leave_room, send

from . import create_app
app = create_app()
socketio = SocketIO(app)


app.config['SITE_NAME'] = 'Something, Anything, that is not that'
app.config['SITE_DESCRIPTION'] = 'a forum for Data to learn from'
app.config['FLASK_DEBUG'] = 1

if __name__ == '__main__':
    socketio.run(app,port=5555, debug=True)

def init_site():
    print("creating initial subforums")
    admin = add_subforum("Forum", "Announcements, bug reports, and general discussion about the forum belongs here")
    add_subforum("Announcements", "View forum announcements here",admin)
    add_subforum("Bug Reports", "Report bugs with the forum here", admin)
    add_subforum("General Discussion", "Use this subforum to post anything you want")
    add_subforum("Other", "Discuss other things here")


def add_subforum(title, description, parent=None):
    sub = Subforum(title, description)
    if parent:
        for subforum in parent.subforums:
            if subforum.title == title:
                return
        parent.subforums.append(sub)
    else:
        subforums = Subforum.query.filter(Subforum.parent_id == None).all()
        for subforum in subforums:
            if subforum.title == title:
                return
        db.session.add(sub)
    print("adding " + title)
    db.session.commit()
    return sub

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)

with app.app_context():
    db.create_all() # TODO this may be redundant
    if not Subforum.query.all():
        init_site()

@app.route('/')
def index():
    subforums = Subforum.query.filter(Subforum.parent_id == None).order_by(Subforum.id)
    return render_template("subforums.html", subforums=subforums)



def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

# @socketio.on('connect')
# def handle_connect():
#     username = session.get('username')
#     room = session.get('room')
#     if username is None or room is None:
#         return
#     if room not in rooms:
#         leave_room(room)
#     join_room(room)
#     send({
#         "sender": "",
#         "message": f"{username} has entered the chat"
#     }, to=room)
#     rooms[room]["members"] += 1
#
# @socketio.on('message')
# def handle_message(payload):
#     room = session.get('room')
#     name = session.get('name')
#     if room not in rooms:
#         return
#     message = {
#             "sender": name,
#             "message": payload["message"]
#         }
#     send(message, to=room)
#     rooms[room]["messages"].append(message)
# @socketio.on('disconnect')
# def handle_disconnect():
#     room = session.get("room")
#     name = session.get("name")
#     leave_room(room)
#     if room in rooms:
#         rooms[room]["members"] -= 1
#         if rooms[room]["members"] <= 0:
#             del rooms[room]
#         send({
#         "message": f"{name} has left the chat",
#         "sender": ""
#     }, to=room)
