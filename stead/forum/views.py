from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from stead import db
from stead.forum.forms import PostForm, CommentForm
from stead.models import Post, User, Comment

forum = Blueprint('forum', __name__)


@forum.route('/forum')
def forums():
    general = Post.query.order_by(Post.date_posted.desc())[0]
    general_num = len(Post.query.all())

    return render_template('forum.html', title='Forum Blog', general=general, general_num=general_num)


@forum.route('/forum/general', methods=['GET', 'POST'])
@login_required
def chat():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(content=form.content.data, user_id=current_user.id)

        db.session.add(post)
        db.session.commit()
        return redirect(url_for('forum.chat'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.date_posted.desc()).paginate(
        page, per_page=10,
        error_out=False)
    posts = pagination
    return render_template('chat_page.html', posts=posts, form=form, title='Forum', show_followed=show_followed, pagination=pagination)


@forum.route('/forum/general/comment/<int:id>', methods=['GET', 'POST'])
@login_required
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('forum.post', id=post.id))
    pagination = post.comments.order_by(Comment.timestamp)

    return render_template('post.html', posts=[post], form=form, comments=pagination, title="Comment")


@forum.route('/forum/user/<username>')
@login_required
def user_posts(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc())
    return render_template('user_forum.html', user=user, posts=posts)


@forum.route("/forum/<int:blog_post_id>/delete")
@login_required
def delete_post(blog_post_id):
    post = Post.query.get_or_404(blog_post_id)
    comment = Comment.query.filter_by(post_id=None).all()
    for n in comment:
        b = Comment.query.get_or_404(n.id)
        db.session.delete(n)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post has been deleted')
    return redirect(url_for('forum.chat'))

