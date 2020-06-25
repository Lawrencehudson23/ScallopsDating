from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import re
import bcrypt
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import random
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


import json
# Create your views here.
def index(request):
    if "user_id" not in request.session:
        return redirect("/login/")

    context = {
        "user" : User.objects.get(id=request.session["user_id"]),
        "all_users" : User.objects.exclude(id=request.session["user_id"]),
    }
    return render(request,'base.html', context)

def display_about_us(request):
    if "user_id" not in request.session:
        return redirect("/login/")

    context = {
        "user" : User.objects.get(id=request.session["user_id"]),
        "all_users" : User.objects.exclude(id=request.session["user_id"]),
    }
    return render(request,'about_us.html',context)

def display_single(request):
    if "user_id" not in request.session:
        return redirect("/login/")
    return render(request,'single.html')
    

def display_contact_us(request):
    if "user_id" not in request.session:
        return redirect("/login/")

    context = {
        "user" : User.objects.get(id=request.session["user_id"]),
        "all_users" : User.objects.exclude(id=request.session["user_id"]),
    }
    return render(request,'contact_us.html',context)
def display_registration(request):
    
    return render(request, 'registration.html')

def process_registration(request):
    errors = User.objects.user_validator(request.POST)
    # realErrors=json.dumps(errors)
    # # print(realErrors['first_name'])
    # print(realErrors)
    # print(json.dumps(errors["first_name"]))

    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
            
        return redirect('/registration/')
    else:
        password = request.POST["password"]
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode() 
        user = User.objects.create(first_name=request.POST["first_name"], last_name=request.POST["last_name"], email=request.POST["email"], password=pw_hash, birthday = request.POST["birthday"], gender=request.POST["gender"], city = request.POST["city"])

        request.session['user_id'] = user.id
        request.session['user_first'] = user.first_name
        return redirect('/')


def process_login(request):
    errors = {}
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

    if not EMAIL_REGEX.match(request.POST['login_email']): 
        errors["login_email"] = "Please enter an email address"

    if len(request.POST['login_password']) < 1:
        errors["login_password"] = "Please enter a password"

    if len(errors)>0:
        for key, value in errors.items():
            messages.error(request,value)
        return redirect('/login/')
    
    user = User.objects.filter(email=request.POST['login_email'])
    if user:
        print("there is a user")
        logged_user = user[0]
        if bcrypt.checkpw(request.POST['login_password'].encode(), logged_user.password.encode()):
            request.session["user_id"] = logged_user.id
            request.session["user_first"] = logged_user.first_name
            return redirect('/')
        else:
            messages.error(request, "Incorrect password")
            return redirect("/login/")
    else:
        messages.error(request,"User does not exist")
    return redirect("/login/")
def process_logout(request):
    request.session.delete()
    return redirect('/login/')
def display_login(request):

    return render(request, 'login.html')

def display_message(request):
    return render(request, 'message.html')

    if "user_id" not in request.session:
        return redirect("/login/")

    context = {
        "user" : User.objects.get(id=request.session["user_id"]),
        "all_users" : User.objects.exclude(id=request.session["user_id"]),
    }
    return render(request, 'message.html',context)
def display_profile(request):
    if "user_id" not in request.session:
        return redirect("/login/")

    context = {
        "user" : User.objects.get(id=request.session["user_id"]),
        "all_users" : User.objects.exclude(id=request.session["user_id"]),
    }
    return render(request, 'profile.html',context)
def display_1on1(request):
    if "user_id" not in request.session:
        return redirect("/login/")

    context = {
        "user" : User.objects.get(id=request.session["user_id"]),
        "all_users" : User.objects.exclude(id=request.session["user_id"]),
    }
    return render(request, '1on1.html',context)

def display_edit_profile(request):
    return render(request, 'edit_profile.html')

def process_profile(request):
    if request.method == 'POST' and request.FILES['imgfile']:
        myfile = request.FILES['imgfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
    
    quick = request.POST
    profile = Profile.objects.create(user = User.objects.get(id = request.session["user_id"]), summary = quick['summary'], interests = quick['interests'], goals = quick['goals'])
    request.session['prof_id'] = profile.id
    context ={
         'uploaded_file_url' : uploaded_file_url,
         'user' : User.objects.get(id = request.session["user_id"]),
         'profile_info' : Profile.objects.get(id =  request.session['prof_id']),
    }    
    return  render (request, 'profile.html', context)
def display_game(request):
    random_id = random.randint(1,44)

    try:
        Game.objects.get(id=random_id)
        question=Game.objects.get(id=random_id)
        print("used try")
    except:
        random_id = random.randint(22,44)
        question = Game.objects.get(id=random_id)
        print("used except")
    
    logged_user = User.objects.get(id=request.session["user_id"])

    context={
        "question":question,
        "logged_user":logged_user,

    }
    return render(request,'game.html', context)


def ajax_game(request):

    logged_user = User.objects.get(id=request.session["user_id"])

    context = {
        'choice' : request.POST["option"],
        "logged_user": logged_user,
    }
    return render(request, 'answer_game.html',context)

def display_message(request):
    logged_user = User.objects.get(id=request.session["user_id"])

    context = {
        'all_messages' : logged_user.messages.all(),
        "logged_user": logged_user,
    }
    return render(request,'message.html', context)

def ajax_message(request):

    logged_user = User.objects.get(id=request.session["user_id"])

    message = Message.objects.create(message=request.POST["message"], user=logged_user, match=Match.objects.get(id=1))

    context = {
        'all_messages' : logged_user.messages.all(),
        "logged_user": logged_user,
    }
    return render(request, 'ajax_message.html',context)




def display_1on1(request):
    if "user_id" not in request.session:
        return redirect("/login/")

    context = {
        "user" : User.objects.get(id=request.session["user_id"]),
        "all_users" : User.objects.exclude(id=request.session["user_id"]),
    }
    return render(request, '1on1.html',context)

# TODO: LIKE DISLIKE
def like(request):
    currentUser= User.objects.get(id=request.session['id'])
    chooseUser=User.objects.get(id=request.session['chooseUser'])
    newLikes=Like.objects.get(liked_by=currentUser).likes().append(chooseUser)
    Like.objects.get(liked_by=currentUser, likes=newLikes)
    return redirect('/1on1/')
def dislike(request):
    pass
    return redirect('/1on1/')
    return render(request, 'profile.html')

def ajax_like(request):
    
    logged_user = User.objects.get(id=request.session["user_id"])
    context = {
        'all_messages' : logged_user.messages.all(),
        "logged_user": logged_user,
    }
    return render(request, 'ajax_message.html',context)


#**********NEW CODE*****************
def chat_index(request):
    return render(request,'chat/index.html', {})

def room(request, room_name):
    context = {
        'room_name': room_name,
        'user_id': request.session["user_id"],
        'first_name':User.objects.get(id=request.session["user_id"]).first_name,
        'last_name':User.objects.get(id=request.session["user_id"]).last_name,
    }
    return render(request, 'chat/room.html', context)


