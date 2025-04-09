
from pyexpat.errors import messages
from flask import render_template, request, redirect, url_for, flash, session
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_user, logout_user
from flask_login.utils import login_required
import datetime
import markdown
from flask import Blueprint, render_template, request, redirect, url_for

from forum.models import User, Post, Comment, Subforum, valid_content, valid_title, db, generateLinkPath, error, Reply

from forum.models import User, Post, Comment, Subforum, valid_content, valid_title, db, generateLinkPath, error, Reply
from forum.user import username_taken, email_taken, valid_username
from markupsafe import Markup
from flask_socketio import join_room, leave_room, send, rooms
from flask_socketio import join_room, leave_room, send, rooms
from werkzeug.security import generate_password_hash, check_password_hash

from roomcode import generate_room_code

from roomcode import generate_room_code

##
# This file needs to be broken up into several, to make the project easier to work on.
##

rt = Blueprint('routes', __name__, template_folder='templates')









@rt.route('/action_login', methods=['POST'])
def action_login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter(User.username == username).first()
    if user and user.check_password(password):
        login_user(user)
    else:
        errors = []
        errors.append("Username or password is incorrect!")
        return render_template("login.html", errors=errors)
    return redirect("/")


# @login_required
@rt.route('/action_logout')
def action_logout():
    #todo
    logout_user()
    return redirect("/")

@rt.route('/action_createaccount', methods=['POST'])
def action_createaccount():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    errors = []
    retry = False
    if username_taken(username):
        errors.append("Username is already taken!")
        retry=True
    if email_taken(email):
        errors.append("An account already exists with this email!")
        retry = True
    if not valid_username(username):
        errors.append("Username is not valid!")
        retry = True
    # if not valid_password(password):
    # 	errors.append("Password is not valid!")
    # 	retry = True
    if retry:
        return render_template("login.html", errors=errors)
    user = User(email, username, password)
    if user.username == "admin":
        user.admin = True
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect("/")


@rt.route('/subforum')
def subforum():
    subforum_id = int(request.args.get("sub"))
    subforum = Subforum.query.filter(Subforum.id == subforum_id).first()
    if not subforum:
        return error("That subforum does not exist!")
    posts = Post.query.filter(Post.subforum_id == subforum_id).order_by(Post.id.desc()).limit(50)
    if not subforum.path:
        subforumpath = generateLinkPath(subforum.id)

    subforums = Subforum.query.filter(Subforum.parent_id == subforum_id).all()
    return render_template("subforum.html", subforum=subforum, posts=posts, subforums=subforums, path=subforumpath)

@rt.route('/loginform')
def loginform():
    return render_template("login.html")


@login_required
@rt.route('/addpost')
def addpost():
    subforum_id = int(request.args.get("sub"))
    subforum = Subforum.query.filter(Subforum.id == subforum_id).first()
    if not subforum:
        return error("That subforum does not exist!")

    return render_template("createpost.html", subforum=subforum)

@rt.route('/viewpost')
def viewpost():
    postid = int(request.args.get("post"))
    post = Post.query.filter(Post.id == postid).first()
    if not post:
        return error("That post does not exist!")
    if not post.subforum.path:
        subforumpath = generateLinkPath(post.subforum.id)
    comments = Comment.query.filter(Comment.post_id == postid).order_by(Comment.id.desc()) # no need for scalability now
    #Turns markdown to HTML

    content_html = markdown.markdown(post.content)

    #Markdown gets rendered here
    return render_template("viewpost.html", post=post, path=subforumpath, comments=comments, content_html=Markup(content_html))

    #Turns markdown to HTML

    content_html = markdown.markdown(post.content)

    #Markdown gets rendered here
    return render_template("viewpost.html", post=post, path=subforumpath, comments=comments, content_html=Markup(content_html))


@login_required
@rt.route('/action_comment', methods=['POST', 'GET'])
def comment():
    post_id = int(request.args.get("post"))
    post = Post.query.filter(Post.id == post_id).first()
    if not post:
        return error("That post does not exist!")
    content = request.form['content']
    postdate = datetime.datetime.now()
    comment = Comment(content, postdate)
    current_user.comments.append(comment)
    post.comments.append(comment)
    db.session.commit()
    return redirect("/viewpost?post=" + str(post_id))





@login_required
@rt.route('/Chat', methods=["GET", "POST"])
def Chat():
    # session.clear()
    # if request.method == "POST":
    #     name = request.form.get('username')
    #     create = request.form.get('create')
    #     code = request.form.get('code')
    #     join = request.form.get('join')
    #     if not name:
    #         return render_template('chat.html', error="Name is required", code=code)
    #
    #     room_code = None
    #
    #     if create is not None:
    #         room_code = generate_room_code(6, [])
    #         new_db_room = Room(room_code=room_code)
    #         db.session.add(new_db_room)
    #         db.session.commit()
    #         # rooms[room_code] = new_room
    #         if room_code not in rooms:
    #             rooms[room_code] = {'members': 0, 'messages':[]}
    #     elif join is not None:
    #         # no code
    #         if not code:
    #             return render_template('chat.html', error="Please enter a room code to enter a chat room", name=name)
    #         # invalid code
    #         existing_room = Room.query.filter_by(room_code=code).first()
    #         if not existing_room:
    #             return render_template('chat.html', error="Room code invalid", name=name)
    #         room_code = code
    #     if room_code:
    #         session['room'] = room_code
    #         session['name'] = name
    #         return redirect(url_for('routes.Room'))
    # else:
        return render_template('chat.html')

#
# @login_required
# @rt.route('/Room')
# def Room():
#     room = session.get('room')
#     name = session.get('username')
#     if name is None or room is None or room not in rooms:
#         return redirect(url_for('Chat'))
#     messages = rooms[room]['messages']
#     return render_template('room.html', room=room, user=name, messages=messages)





# #implement like comments but on user instead of post
# @login_required
# @rt.route('/action_message', methods=['POST'])
# def message():
#    user_id = int(request.args.get("user"))
#    user = User.query.filter(User.id == user_id).first()
#    if not user:
#        return error("This user does not exist!")
#    content = request.form['content']
#    postdate = datetime.datetime.now()
#    message = Message(content, postdate)
#    current_user.messages.append(message)
#    user.messages.append(message)
#    db.session.commit()
#    return redirect(url_for('routes.Chat', post=message.user_id))
@rt.route('/Chat', methods=["GET", "POST"])
def Chat():
    # session.clear()
    # if request.method == "POST":
    #     name = request.form.get('username')
    #     create = request.form.get('create')
    #     code = request.form.get('code')
    #     join = request.form.get('join')
    #     if not name:
    #         return render_template('chat.html', error="Name is required", code=code)
    #
    #     room_code = None
    #
    #     if create is not None:
    #         room_code = generate_room_code(6, [])
    #         new_db_room = Room(room_code=room_code)
    #         db.session.add(new_db_room)
    #         db.session.commit()
    #         # rooms[room_code] = new_room
    #         if room_code not in rooms:
    #             rooms[room_code] = {'members': 0, 'messages':[]}
    #     elif join is not None:
    #         # no code
    #         if not code:
    #             return render_template('chat.html', error="Please enter a room code to enter a chat room", name=name)
    #         # invalid code
    #         existing_room = Room.query.filter_by(room_code=code).first()
    #         if not existing_room:
    #             return render_template('chat.html', error="Room code invalid", name=name)
    #         room_code = code
    #     if room_code:
    #         session['room'] = room_code
    #         session['name'] = name
    #         return redirect(url_for('routes.Room'))
    # else:
        return render_template('chat.html')

#
# @login_required
# @rt.route('/Room')
# def Room():
#     room = session.get('room')
#     name = session.get('username')
#     if name is None or room is None or room not in rooms:
#         return redirect(url_for('Chat'))
#     messages = rooms[room]['messages']
#     return render_template('room.html', room=room, user=name, messages=messages)





# #implement like comments but on user instead of post
# @login_required
# @rt.route('/action_message', methods=['POST'])
# def message():
#    user_id = int(request.args.get("user"))
#    user = User.query.filter(User.id == user_id).first()
#    if not user:
#        return error("This user does not exist!")
#    content = request.form['content']
#    postdate = datetime.datetime.now()
#    message = Message(content, postdate)
#    current_user.messages.append(message)
#    user.messages.append(message)
#    db.session.commit()
#    return redirect(url_for('routes.Chat', post=message.user_id))





@login_required
@rt.route('/action_reply/comment/<int:comment_id>', methods=['POST']) #attempt to mimic comment as a reply
def action_reply(comment_id):
	comment = Comment.query.get_or_404(comment_id)
	content = request.form['content']
	postdate = datetime.datetime.now()
	reply = Reply(content=content, postdate=postdate, user_id=current_user.id, comment_id=comment_id)
	db.session.add(reply)
	db.session.commit()
	return redirect(url_for('routes.viewpost', post=comment.post_id))


@login_required
@rt.route('/action_post', methods=['POST'])
def action_post():
    subforum_id = int(request.args.get("sub"))
    subforum = Subforum.query.filter(Subforum.id == subforum_id).first()
    if not subforum:
        return redirect(url_for("subforums"))
    user = current_user
    title = request.form['title']
    content = request.form['content']
    content_html = markdown.markdown(content)
    print(f"Generated HTML: {content}")
    #check for valid posting
    errors = []
    retry = False
    if not valid_title(title):
      errors.append("Title must be between 4 and 140 characters long!")
      retry = True
    if not valid_content(content):
      errors.append("Post must be between 10 and 5000 characters long!")
      retry = True
    if retry:
      return render_template("createpost.html", content_html=Markup(content_html), subforum=subforum,  errors=errors)
    post = Post(title, content, datetime.datetime.now())
    subforum.posts.append(post)
    user.posts.append(post)
    db.session.commit()
    return redirect("/viewpost?post=" + str(post.id))




@login_required
@rt.route('/user')
def user():
	user_id = request.args.get('user_id')

	if user_id:
		user = User.query.get_or_404(user_id)
		posts = Post.query.filter(Post.user_id == user.id).all()
		comments = Comment.query.filter(Comment.user_id == user.id).all()
		replies = Reply.query.filter(Reply.user_id == user.id).all()
		return render_template('user.html', user=user, posts=posts, comments= comments, replies= replies)
	elif current_user.is_authenticated:
		return redirect(url_for('routes.user', user_id=current_user.id))
	else:
		return redirect ('/loginform')



@login_required
@rt.route('/change_password', methods=['POST', 'GET'])
def change_password():
	if request.method == 'POST':
		old_password = request.form['old_password']
		new_password = request.form['new_password']
		confirm_password = request.form['confirm_password']

		if not check_password_hash(current_user.password_hash, old_password):
			flash('Old password does not match records.', 'danger')
			return redirect(url_for('routes.change_password'))

		if new_password != confirm_password:
			flash('New and confirm do not match.', 'warning')
			return redirect(url_for('routes.change_password'))

		current_user.password_hash = generate_password_hash(new_password)
		db.session.commit()

		flash('Password has been updated', 'success')
		return redirect(url_for('routes.change_password'))

	return render_template('change_password.html')
