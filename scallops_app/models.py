from django.db import models
import re
from datetime import datetime

class UserManager(models.Manager):
    def user_validator(self, post_Data):
        errors = {}

        if len(post_Data["first_name"]) < 2:
            errors["first_name"] = "First name must be longer than two letters"
        elif post_Data["first_name"].isalpha() == False:
            errors["first_name"] = "First name can only contain letters"

        if len(post_Data["last_name"]) < 2:
            errors["last_name"] = "Last name must be longer than two letters"
        elif post_Data["last_name"].isalpha() == False:
            errors["last_name"] = "Last name can only contain letters"
        
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(post_Data['email']):          
            errors['email'] = "Invalid email address!"
        
        if len(post_Data["password"]) < 8:
            errors['password'] = "Password must have at least 8 characters"

        if post_Data["password"] != post_Data["pass_confirm"]:
            errors['pass_confirm'] = "Passwords do not match!"
        
        return errors

# Create your models here.
class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    birthday = models.DateField(null=True, auto_now=False)
    gender = models.CharField(null=True, max_length=200)
    city = models.CharField(null=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    def __str__(self):
        return "<User: {} {}>".format(self.first_name, self.last_name)

    def __repr__(self):
       return self.__str__()

class Like(models.Model):
    likes = models.ForeignKey(User, related_name="likes", on_delete=models.CASCADE)
    liked_by = models.ForeignKey(User, related_name="liked_by", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Match(models.Model):
    user1 = models.ForeignKey(User, related_name="match1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name="match2", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

#creating model for messaging
# class Message(models.Model):
#     sender = models.ForeignKey(User, related_name= 'send', on_delete=models.CASCADE)
#     receiver = models.ForeignKey(User, related_name= 'receive', on_delete=models.CASCADE)
#     r_msg = models.TextField()
#     sender_msg = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


class Profile(models.Model):
    # image = models.ImageField(default = 'static/images/default.png')
    user = models.OneToOneField(User, related_name='my_profile', on_delete=models.CASCADE)
    summary = models.TextField(default = 'Nothing to display')
    interest = models.TextField(default = 'Nothing to display')
    goals = models.TextField(default = 'Nothing to display')
    updated_at = models.DateTimeField(auto_now_add=True)
# class Profile(models.Model):
#     image = models.ImageField(width_field=200px, height_field=400px)
#     summary = models.TextField()
#     interest = models.TextField()
#     goals = models.TextField()
# class Profile(models.Model):
#     # image = models.ImageField(width_field=200px, height_field=400px)
#     summary = models.TextField()
#     interest = models.TextField()
#     goals = models.TextField()

class Game(models.Model):
    option1 = models.CharField(max_length=1000)
    option2 = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    message = models.TextField()
    user = models.ForeignKey(User, related_name="messages", on_delete=models.CASCADE)
    match = models.ForeignKey(Match, related_name="messages", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)





