from flask import current_app
import os
from PIL import Image


def savebus_picture(form_picture,form_busname):
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = form_busname + f_ext
    picture_path = os.path.join(current_app.root_path,'static/img',picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn