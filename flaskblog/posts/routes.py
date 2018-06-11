from flask import (render_template, url_for, flash,
                   redirect, request, jsonify ,abort, Blueprint)
from flask_login import current_user, login_required
from flaskblog import db,bcrypt
from flaskblog.models import Post,Comment,Like,Dislike,LikeComment,DislikeComment
from flaskblog.posts.forms import PostForm, CommentForm
from flaskblog.users.utils import save_picture

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            post.post_image = picture_file
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.date_posted.desc()).paginate(page=page, per_page=5)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, author=current_user,post_id=post_id)
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            comment.comment_image = picture_file
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been created!', 'success')
        return redirect(url_for('posts.post',post_id=post.id))
    return render_template('post.html', title=post.title, post=post, form=form, comments=comments,legend='Leave a comment')


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            post.post_image = picture_file
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')



def delete_all_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id)
    for comment in comments:
        commentlikes = LikeComment.query.filter_by(comment_id=comment.id)
        for commentlike in commentlikes:
            db.session.delete(commentlike)

        commentdislikes = DislikeComment.query.filter_by(comment_id=comment.id)
        for commentdislike in commentdislikes:
            db.session.delete(commentdislike)
        db.session.delete(comment)

def delete_all_likes_and_dislikes(post_id):
    likes = Like.query.filter_by(post_id=post_id)
    for like in likes:
        db.session.delete(like)

    dislikes = Dislike.query.filter_by(post_id=post_id)
    for dislike in dislikes:
        db.session.delete(dislike)

@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    delete_all_comments(post_id)
    delete_all_likes_and_dislikes(post_id)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))

@posts.route("/post/<int:post_id>/<int:comment_id>/delete", methods=['POST'])
@login_required
def delete_comment(comment_id,post_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user:
        abort(403)
    db.session.delete(comment)
    delete_all_likes_and_dislikes(comment_id)
    db.session.commit()
    flash('Your comment has been deleted!', 'success')
    return redirect(url_for('posts.post',post_id=post_id))


@posts.route('/like/', methods=['GET','POST'])
@login_required
def like():
    num = float(request.form.get('number', 0))
    dislikecount = float(request.form.get('dislikecount', 0))
    post_id = request.form.get('post_id',0)
    likesearch = Like.query.filter_by(user_id=current_user.id,post_id=post_id).first()
    dislikesearch = Dislike.query.filter_by(user_id=current_user.id,post_id=post_id).first()

    if likesearch is None:
        post = Post.query.get_or_404(post_id)
        post.likes_count+=1
        like = Like(user_id=current_user.id,post_id=post_id)

        if dislikesearch is None:
            pass
        else:
            post.dislikes-=1
            dislikecount-=1
            db.session.delete(dislikesearch)

        db.session.add(like)
        db.session.commit()
        result = num + 1
        data = {'result': result,'dislikecount':dislikecount,'color':"Green"}
        data = jsonify(data)
        return data
    else:
        post = Post.query.get_or_404(post_id)
        post.likes_count-=1
        db.session.delete(likesearch)
        db.session.commit()
        result = num - 1
        data = {'result': result,'color':"Red"}
        data = jsonify(data)
        return data

@posts.route('/dislike/', methods=['GET','POST'])
@login_required
def dislike():
    num = float(request.form.get('number', 0))
    likecount = float(request.form.get('likecount', 0))
    post_id = request.form.get('post_id',0)
    dislikesearch = Dislike.query.filter_by(user_id=current_user.id,post_id=post_id).first()
    likesearch = Like.query.filter_by(user_id=current_user.id,post_id=post_id).first()

    if dislikesearch is None:
        post = Post.query.get_or_404(post_id)
        post.dislikes+=1
        if likesearch is None:
            pass
        else:
            post.likes_count-=1
            likecount-=1
            db.session.delete(likesearch)

        dislike = Dislike(user_id=current_user.id,post_id=post_id)
        db.session.add(dislike)
        db.session.commit()
        result = num + 1
        data = {'result': result,'likecount':likecount,'color':"Green"}
        data = jsonify(data)
        return data
    else:
        post = Post.query.get_or_404(post_id)
        post.dislikes-=1
        db.session.delete(dislikesearch)
        db.session.commit()
        result = num - 1
        data = {'result': result,'color':"Red"}
        data = jsonify(data)
        return data

@posts.route('/comment/like', methods=['GET','POST'])
@login_required
def like_comment():
    num = float(request.form.get('number', 0))
    dislikecount = float(request.form.get('dislikecount', 0))
    comment_id = request.form.get('comment_id',0)
    likesearch = LikeComment.query.filter_by(user_id=current_user.id,comment_id=comment_id).first()
    dislikesearch = DislikeComment.query.filter_by(user_id=current_user.id,comment_id=comment_id).first()

    if likesearch is None:
        comment = Comment.query.get_or_404(comment_id)
        comment.likes_count+=1
        like = LikeComment(user_id=current_user.id,comment_id=comment_id)

        if dislikesearch is None:
            pass
        else:
            comment.dislikes-=1
            dislikecount-=1
            db.session.delete(dislikesearch)

        db.session.add(like)
        db.session.commit()
        result = num + 1
        data = {'result': result,'dislikecount':dislikecount,'color':"Green"}
        data = jsonify(data)
        return data
    else:
        comment = Comment.query.get_or_404(comment_id)
        comment.likes_count-=1
        db.session.delete(likesearch)
        db.session.commit()
        result = num - 1
        data = {'result': result,'color':"Red"}
        data = jsonify(data)
        return data

@posts.route('/comment/dislike', methods=['GET','POST'])
@login_required
def dislike_comment():
    num = float(request.form.get('number', 0))
    likecount = float(request.form.get('likecount', 0))
    comment_id = request.form.get('comment_id',0)
    dislikesearch = DislikeComment.query.filter_by(user_id=current_user.id,comment_id=comment_id).first()
    likesearch = LikeComment.query.filter_by(user_id=current_user.id,comment_id=comment_id).first()

    if dislikesearch is None:
        comment = Comment.query.get_or_404(comment_id)
        comment.dislikes+=1
        if likesearch is None:
            pass
        else:
            comment.likes_count-=1
            likecount-=1
            db.session.delete(likesearch)

        dislike = DislikeComment(user_id=current_user.id,comment_id=comment_id)
        db.session.add(dislike)
        db.session.commit()
        result = num + 1
        data = {'result': result,'likecount':likecount,'color':"Green"}
        data = jsonify(data)
        return data
    else:
        comment = Comment.query.get_or_404(comment_id)
        comment.dislikes-=1
        db.session.delete(dislikesearch)
        db.session.commit()
        result = num - 1
        data = {'result': result,'color':"Red"}
        data = jsonify(data)
        return data
