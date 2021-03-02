import os
import secrets
# pip install pillow
from PIL import Image
from stead import app
from stead.models import User
from stead.news_posts.models import NewsPost



def save_picture(form_picture, location, out_size):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    pic_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, f'static/{location}', pic_fn)
    out_size = out_size
    i = Image.open(form_picture)
    i.thumbnail(out_size)
    i.save(picture_path)

    return pic_fn


def residue_profile_pics():
    new_folder = []
    image = []
    for filename in os.listdir(os.path.join(app.root_path, 'static/profile_pics')):
        new_folder.append(filename)
    user = User.query.order_by(User.id)
    for u in user:
        image.append(u.profile_image)
    for i in new_folder:
        if i not in image:
            os.unlink(os.path.join(app.root_path, f'static/profile_pics/{i}'))


def residue_news_pics():
    new_folder = []
    image = []
    for filename in os.listdir(os.path.join(app.root_path, 'static/news_pic')):
        new_folder.append(filename)
    user = NewsPost.query.order_by(NewsPost.id)
    for u in user:
        image.append(u.picture)
    for i in new_folder:
        if i not in image:
            os.unlink(os.path.join(app.root_path, f'static/news_pic/{i}'))


