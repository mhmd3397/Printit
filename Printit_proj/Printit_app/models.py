import re
import bcrypt
from django.db import models


class UserManager(models.Manager):
    def basic_validator_registration(self, postData):
        errors = {}
        # Validate First Name
        first_name = postData.get('first_name')
        if not first_name:
            errors['first_name'] = "First name is required."
        elif len(first_name) < 2:
            errors['first_name'] = "First name should be at least 2 characters."  # noqa

        # Validate Last Name
        last_name = postData.get('last_name')
        if not last_name:
            errors['last_name'] = "Last name is required."
        elif len(last_name) < 2:
            errors['last_name'] = "Last name should be at least 2 characters."

        # Validate Email
        EMAIL_REGEX = re.compile(
            r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        email = postData.get('email')
        if not email:
            errors['email'] = "Email is required."
        elif not EMAIL_REGEX.match(postData['email']):
            errors['email'] = "Invalid email format."
        if User.objects.filter(email=email).exists():
            errors['email'] = "This email is already registered."

        # Validate Password
        password = postData.get('password')
        confirm_password = postData.get('confirm_password')
        if not password:
            errors['password'] = "Password is required."
        elif len(password) < 8:
            errors['password'] = "Password should be at least 8 characters."
        elif password != confirm_password:
            errors['confirm_password'] = "Passwords do not match."

        # Validate Bio (Optional)
        bio = postData.get('bio')
        if bio and len(bio) < 10:
            errors['bio'] = "Bio should be at least 10 characters."

        return errors

    def basic_validator_login(self, postData):
        errors = {}
        # Validate Email
        email = postData.get('email')
        user = User.objects.filter(email=email).first()
        if not user:
            errors['email'] = "Your email or password is incorrect."
        # Validate Password
        if user and not bcrypt.checkpw(postData.get('password').encode(), user.password.encode()):  # noqa
            errors['password'] = "Your email or password is incorrect."

        return errors


class User(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    bio = models.TextField(blank=True, null=True)

    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()


class IdeaManager(models.Manager):
    def basic_validator_idea(self, postData):
        errors = {}
        # Validate title and content
        title = postData.get('title')
        content = postData.get('content')
        if not title:
            errors['title'] = "Title is required."
        elif len(title) < 5:
            errors['title'] = "Title should be at least 5 characters."

        if not content:
            errors['content'] = "Content is required."
        elif len(content) < 10:
            errors['content'] = "Content should be at least 10 characters."

        return errors


class Idea(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = IdeaManager()


class CommentManager(models.Manager):
    def basic_validator_comment(self, postData):
        errors = {}
        # Validate text
        text = postData.get('text')
        if not text:
            errors['text'] = "Comment text is required."
        elif len(text) < 10:
            errors['text'] = "Comment text should be at least 10 characters."

        return errors


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CommentManager()


class StarManager(models.Manager):
    def basic_validator_star(self, postData):
        errors = {}
        # Validate stars
        stars = postData.get('stars')
        if not stars:
            errors['stars'] = "Stars field is required."
        elif not stars.isdigit():
            errors['stars'] = "Stars must be an integer."
        else:
            stars = int(stars)
            if stars < 1 or stars > 5:
                errors['stars'] = "Stars must be between 1 and 5."

        return errors


class Star(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    stars = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = StarManager()
