from flask import render_template,url_for,flash, redirect,request,Blueprint, abort
from flask_login import current_user,login_required
from stead import db, app
from flask_uploads import configure_uploads, UploadSet, IMAGES
from stead.news_posts.models import NewsPost
from stead.models import User
from stead.news_posts.forms import NewPostForm
from stead.decorator import admin_required, permission_required
from stead.users.picture_handler import save_picture, residue_news_pics

news_posts = Blueprint('news_posts', __name__)

news = UploadSet('news', IMAGES)
app.config['UPLOADED_NEWS_DEST'] = 'stead/static/news_pic'
upload = configure_uploads(app,  news)


@news_posts.route('/news')
@login_required
def news():
    '''
    This is the home page view. Notice how it uses pagination to show a limited
    number of posts by limiting its query size and then calling paginate.
    '''
    page = request.args.get('page', 1, type=int)
    blog_posts = NewsPost.query.order_by(NewsPost.date.desc()).paginate(page=page, per_page=10)
    return render_template('all_news.html', blog_posts=blog_posts)


@news_posts.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_post():
    form = NewPostForm()

    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data, 'news_pic', (600, 600))
        blog_post = NewsPost(title=form.title.data,
                             text=form.text.data,
                             user_id=current_user.id,
                             picture=picture_file
                             )
        db.session.add(blog_post)
        db.session.commit()
        flash("Blog Post Created")
        return redirect(url_for('core.home'))

    return render_template('blogpage.html', form=form)


# int: makes sure that the blog_post_id gets passed as in integer
# instead of a string so we can look it up later.
@news_posts.route('/<int:blog_post_id>')
@login_required
def blog_post(blog_post_id):
    # grab the requested blog post by id number or return 404
    blog_post = NewsPost.query.get_or_404(blog_post_id)
    return render_template('blog_post.html', title=blog_post.title,
                            date=blog_post.date, post=blog_post
    )


@news_posts.route("/<int:blog_post_id>/update", methods=['GET', 'POST'])
@login_required
@admin_required
def update(blog_post_id):
    blog_post = NewsPost.query.get_or_404(blog_post_id)
    if blog_post.author != current_user:
        # Forbidden, No Access
        abort(403)

    form = NewPostForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data, 'news_pic', (600, 600))
        blog_post.title = form.title.data
        blog_post.text = form.text.data
        blog_post.picture = picture_file
        db.session.commit()
        residue_news_pics()
        flash('Post Updated')
        return redirect(url_for('news_posts.blog_post', blog_post_id=blog_post.id))
    # Pass back the old blog post information so they can start again with
    # the old text and title.
    elif request.method == 'GET':
        form.title.data = blog_post.title
        form.text.data = blog_post.text
    return render_template('blogpage.html', title='Update',
                           form=form)


@news_posts.route("/<username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    blog_posts = NewsPost.query.filter_by(author=user).order_by(NewsPost.date.desc()).paginate(page=page, per_page=5)
    return render_template('all_news.html', blog_posts=blog_posts, user=user)


@news_posts.route("/<int:blog_post_id>/delete", methods=['POST'])
@login_required
@admin_required
def delete_post(blog_post_id):
    blog_post = NewsPost.query.get_or_404(blog_post_id)
    if blog_post.author != current_user:
        abort(403)
    db.session.delete(blog_post)
    db.session.commit()
    residue_news_pics()
    flash('Post has been deleted')
    return redirect(url_for('core.home'))
