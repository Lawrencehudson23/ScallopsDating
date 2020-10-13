from django.db import models
import re
from datetime import datetime
from django.db.models import Q


class UserManager(models.Manager):
    def user_validator(self, post_Data):
        errors = {}
        # if not 'formtype' in post_Data:
        #     return False
        # if post_Data['formtype']=='register':
        #     user_data=User.objects.filter(email=post_Data['email'])
        #     if not user_data:
        #         pass
        if len(post_Data["first_name"]) < 2:
            errors["first_name"] = "First name must be longer than two letters"
        elif post_Data["first_name"].isalpha() == False:
            errors["first_name"] = "First name can only contain letters"

        if len(post_Data["last_name"]) < 2:
            errors["last_name"] = "Last name must be longer than two letters"
        elif post_Data["last_name"].isalpha() == False:
            errors["last_name"] = "Last name can only contain letters"
        if not 'gender' in post_Data:
            errors['gender'] = " You must select a gender option."
        if not 'city' in post_Data:
            errors['city'] = " You must select a city option."
        if post_Data['birthday'] == '':
            errors['birthday'] = 'You must enter a birthday.'

        elif post_Data['birthday'] != '':
            current_date = (datetime.now())
            birthday = datetime.strptime(post_Data['birthday'], "%Y-%m-%d")
            days = current_date - birthday
            if days.days < 6570 and days.days > 0:
                errors['birthday'] = 'You must be 18 or older to sign up.'

            elif days.days < 0:
                errors['birthday'] = 'You cannot select a date that has not occurred yet.'

        EMAIL_REGEX = re.compile(
            r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(post_Data['email']):
            errors['email'] = "Invalid email address!"

        if len(post_Data["password"]) < 8:
            errors['password'] = "Password must have at least 8 characters"
        if len(post_Data["pass_confirm"]) < 8:
            errors['password'] = "Confirm Password must have at least 8 characters"
        elif post_Data["password"] != post_Data["pass_confirm"]:
            errors['password'] = "Password does not match confirmed password."

        # elif post_Data['formtype'] == 'login':
        #     user_data = User.objects.filter(email_address=post_Data['email_address'])
        #     if not emailregex.match(post_Data['email_address']) and post_Data['email_address'] != '':
        #         errors['email_address'] = 'Invalid email address.'

        #     elif not user_data and post_Data['email_address'] == '':
        #          errors['email_address'] = 'Email field cannot be empty.'

        #     elif not user_data:
        #         errors['email_address'] = 'That email address does not exist.'

        #     user_data = User.objects.get(email_address=post_Data['email_address'])
        #     password = bcrypt.checkpw(post_Data['password'].encode(), user_data.password.encode())
        #     if len(post_Data['password']) <= 0:
        #         errors['password'] = 'Password field cannot be empty.'

        #     elif post_Data['email_address'] != user_data.email_address or password != True:
        #         errors['password'] = 'Your email and password do not match. Please try again.'

        # elif post_Data['formtype'] == 'update':
        #     if post_Data['password'] == '':
        #         return errors
        #     else:
        #         if len(post_Data['password']) < 9:
        #             errors['password'] = 'Password must be more than 8 characters.'
        #         elif len(post_Data['passwordcheck']) < 9:
        #             errors['password'] = 'Confirmed password must be more than 8 characters.'

        #         elif post_Data['password'] != post_Data['passwordcheck']:
        #             errors['password'] = 'Password does not match password confirmation.'

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

    likes = models.ManyToManyField(
        "self", related_name="liked_by", symmetrical=False)
    skips = models.ManyToManyField("self", related_name="skipped_by")
    matches = models.ManyToManyField("self", through="Match")

    objects = UserManager()

    def __str__(self):
        return "<User: {} {}>".format(self.first_name, self.last_name)

    def __repr__(self):
        return self.__str__()

    def likes_list(self):
        return self.likes.all()

    def liked_by_list(self):
        return self.liked_by.all()

    def unlike(self, unliked_user_id):
        user_id = self.id
        unliked_user = User.objects.get(id=unliked_user_id)
        self.likes.remove(unliked_user)

        self.matches.remove(unliked_user)
        print("match deleted")


class Profile(models.Model):
    image = models.ImageField(default='/images/avator.jpg', upload_to='images')
    summary = models.TextField(default='Nothing to display')
    interest = models.TextField(default='Nothing to display')
    goals = models.TextField(default='Nothing to display')
    user = models.OneToOneField(
        to=User, on_delete=models.CASCADE, primary_key=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    content = models.TextField()
    author = models.ForeignKey(
        User, related_name="author_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        User, related_name="received_messages", on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.author.first_name

    def last_10_messages(self):
        return self.object.order_by('-created_at').all()[:10]



class Match(models.Model):
    user1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="match1")
    user2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="match2")
    messages = models.ManyToManyField(Message, related_name="matches")
    created_at = models.DateTimeField(auto_now_add=True)
