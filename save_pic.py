import os
from password_generator import PasswordGenerator
pwo = PasswordGenerator()
pwo.minlen = 10 # (Optional)
pwo.maxlen = 30


def save_picture(location , form_picture):
    hashed_caption = pwo.generate()
    f_name,f_ext = os.path.splitext(form_picture.filename)
    f_ext = str(f_ext)
    print(f_ext)
    if(f_ext not in ['.jpg' , '.jpeg' , '.png' , '.psd' , '.ai']):
        return 0
    fn = hashed_caption + f_name
    picture_fn = fn + f_ext
    picture_path = os.path.join(location , 'static/task_pictures_instructor' , picture_fn)
    form_picture.save(picture_path)
    return picture_fn

def save_picture_student(location , form_picture):
    hashed_caption = pwo.generate()
    f_name,f_ext = os.path.splitext(form_picture.filename)
    if(f_ext not in ['.jpg' , '.jpeg' , '.png' , '.psd' , '.ai']):
        return 0
    fn = hashed_caption + f_name
    picture_fn = fn + f_ext
    picture_path = os.path.join(location , 'static/task_pictures_student' , picture_fn)
    form_picture.save(picture_path)
    return picture_fn