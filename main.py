from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from werkzeug.urls import url_encode
import datetime
import smtplib

my_email = "safcoding008@gmail.com"
password = "hzww ujoo lwui yooa"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

class BlogPostForm(FlaskForm):
    blog_title = StringField("Blog Post Title", validators=[DataRequired(message="Field is empty")])
    blog_subtitle = StringField("Subtitle", validators=[DataRequired(message="Field is empty")])
    blog_author = StringField("Your name", validators=[DataRequired(message="Field is empty")])
    blog_image_url = URLField("Blog Image URL", validators=[DataRequired(message="Field is empty")])
    blog_content = CKEditorField("Blog Content", validators=[DataRequired(message="Field is empty")])
    blog_submit = SubmitField("Submit Post", validators=[DataRequired(message="Submit credentials")])


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    posts = []
    result = db.session.execute(db.select(BlogPost))
    all_posts = result.scalars().all()
    for post in all_posts:
        posts.append(post)
    return render_template("index.html", all_posts=posts)

# TODO: Add a route so that you can click on individual posts.
@app.route('/<int:post_id>')
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    result = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id))
    requested_post = result.scalar()
    return render_template("post.html", post=requested_post)

# TODO: add_new_post() to create a new blog post
@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    form = BlogPostForm()
    new_post = BlogPost(
        title=request.form.get('blog_title'),
        subtitle=request.form.get('blog_subtitle'),
        date=datetime.datetime.now().strftime("%B %d, %Y"),
        body=request.form.get('blog_content'),
        author=request.form.get('blog_author'),
        img_url=request.form.get('blog_image_url'))
    if form.validate_on_submit():
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form)

# TODO: edit_post() to change an existing blog post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = BlogPostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body)
    if edit_form.validate_on_submit():
        post.title = request.form.get('blog_title')
        post.subtitle = request.form.get('blog_subtitle')
        post.img_url = request.form.get('blog_image_url')
        post.author = request.form.get('blog_author')
        post.body = request.form.get('blog_content')
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))
    return render_template('make-post.html', form=edit_form, is_edit=True)

# TODO: delete_post() to remove a blog post from the database
@app.route("/delete/<int:post_id>", methods=["GET", "POST"])
def delete_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    name = request.form.get('name')
    email_address = request.form.get('email')
    phone_number = request.form.get('phone')
    message = request.form.get('message')
    if request.method == "POST":
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=my_email,
                                to_addrs="fermansamir@gmail.com",
                                msg=f"Subject: Contact Message!\n\n"
                                    f"Name: {name}\n"
                                    f"Email Address: {email_address}\n"
                                    f"Phone Number: {phone_number}\n\n"
                                    f"{message}")
            return render_template("contact.html", message_sent=True)
    return render_template("contact.html", message_sent=False)


if __name__ == "__main__":
    app.run(debug=True, port=5003)
