from flask import current_app
import os
import  secrets
from PIL import Image
import random



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path,'static/profile_pics',picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

def generate_ticket_no(date):
    mylist = list(range(1000,2000))
    random.shuffle(mylist)
    ran_num = mylist.pop()
    date = date.strftime("%Y%m%d")
    return f"TRIP-{date}-{ran_num}"

