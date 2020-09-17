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
from django.db.models import Q, Count, Max


import json
# Create your views here.
def index(request):
    if "user_id" not in request.session:
        return redirect("/login/")
    print("logged user is: "+ str(request.session["user_id"]))

    context = {
        "user" : User.objects.get(id=request.session["user_id"]),
        "all_users" : User.objects.exclude(id=request.session["user_id"]),
        "user_id" : request.session["user_id"],
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
            print("user id is: "+ str(logged_user.id))
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

    logged_user = User.objects.get(id=request.session["user_id"])

    try:
        all_users = User.objects.exclude(id=logged_user.id).order_by("created_at")
        liked_already = logged_user.likes.all().order_by("created_at")
        not_yet_liked = []

        i = 0
        j= 0 
        while j < len(liked_already):
            if liked_already[j] == all_users[i]:
                j+=1
            else:
                not_yet_liked.append(all_users[i])
            i+=1
    
        not_yet_liked.extend(all_users[i:len(all_users)])
        print("THIS IS NOT YET LIKED LIST") 
        print(not_yet_liked)

        skipped_already = logged_user.skips.all().order_by("created_at")
        print("THIS IS SKIPPED LIST")
        print(skipped_already)
        i = 0
        j= 0 
        while j < len(skipped_already) and i < len(not_yet_liked):
            if skipped_already[j] == not_yet_liked[i]:
                del not_yet_liked[i]
                j+=1
            else:
                j+=1

        if len(not_yet_liked) < 1:
            return render(request, '1on1error.html')

        context = {
            "user" : logged_user,
            "potential": not_yet_liked[random.randint(0,(len(not_yet_liked)-1))],
            "user_id" : logged_user.id,
        }
        print(context["potential"])
        return render(request, '1on1.html',context)
    except:
        return redirect("/")

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

# TODO: LIKE DISLIKE
def like(request):
    currentUser= User.objects.get(id=request.session['user_id'])
    likedUser=User.objects.get(id=request.POST['liked'])
    currentUser.likes.add(likedUser)
    likedList = likedUser.likes.all()
    for user in likedList:
        if user == currentUser:
            currentUser.matches.add(likedUser)
            print('theres a match!')
            messages.info(request,"You matched with "+ likedUser.first_name)
            return redirect('/1on1/')
        
    return redirect('/1on1/')

def skip(request):
    currentUser = User.objects.get(id=request.session['user_id'])
    skippedUser = User.objects.get(id=request.POST['skipped'])
    currentUser.skips.add(skippedUser)
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

def toRoom(request, room_name, user_id):
    if "user_id" not in request.session:
        return redirect("/login/")
    logged_user = User.objects.get(id=request.session['user_id'])
    if logged_user.id != user_id:
        return redirect('/login')
    newest_msg = Message.objects.filter( Q(author__id = user_id) | Q(recipient__id = user_id)).order_by('-created_at').all()[:1]
    try:
        if newest_msg:
            newest_msg = newest_msg[0]
            if newest_msg.author.id == logged_user.id:
                matched_user = newest_msg.recipient
            else:
                matched_user = newest_msg.author
        else:
            matched_user = logged_user.matches.all().order_by('-created_at').all()[:1]
            matched_user = matched_user[0]
    except:
        return render(request, 'chatError.html')

    # match = Match.objects.get(user1=logged_user.id, user2=matched_user.id)
    match = Match.objects.filter( Q(user1=logged_user.id, user2=matched_user.id) | Q(user1=matched_user.id, user2=logged_user.id)).order_by('id').all()[:1]
    # match_id = match.id
    # match2 = Match.objects.get(user1=matched_user[0].id, user2=logged_user.id)
    # if match.id < match2.id:
    #     match_id = match.id
    # else:
    #     match_id = match2.id
    return redirect ('/chat/'+ room_name + '/' + str(user_id) + '/' + str(match[0].id))



def room(request, room_name, user_id, match_id):
    if "user_id" not in request.session:
        return redirect("/login/")
    logged_user = User.objects.get(id=request.session['user_id'])
    if logged_user.id != user_id:
        return redirect('/login')
    user1 = Match.objects.get(id=match_id).user1
    user2 = Match.objects.get(id=match_id).user2
    if user1 == logged_user:
        matched_user = user2
    else:
        matched_user = user1
    # match = Match.objects.get(user1=logged_user.id, user2=matched_user.id)
    # match2 = Match.objects.get(user1=matched_user.id, user2=logged_user.id)
    # if match.id < match2.id:
    #     match_id = match.id
    # else:
    #     match_id = match2.id
    # matches = Match.objects.filter(user1 = user_id).order_by('-created_at').all()[:10]
    # logged_user.matches.all().order_by('-created_at').all()
    # messages = Message.objects.filter( Q(author__id = user_id) | Q(recipient__id = user_id)).order_by('-created_at').all()[:10] 

    # matches = Match.objects.filter(user1 = user_id).annotate(mcount = Count('messages')).order_by('-created_at').all()[:15]  
    matches = Match.objects.filter(user1 = user_id).order_by('messages').all()[:15]
    matches = Match.objects.filter(user1=user_id).annotate(message = Max('messages')).order_by('-message').all()[:15]

    print(matches)
    new_messages = []
    match_with_no_msgs = []
    for match in matches:
        message = match.messages.order_by('-created_at').all()[:1]
        if match.id > Match.objects.get(user1=match.user2.id, user2=user_id).id:
            matchId = Match.objects.get(user1=match.user2.id, user2=user_id).id
        else:
            matchId = match.id
        if len(message)>0:
            new_messages.append({
                "match_id" : matchId,
                # MATCH ID NEEDS TO BE SMALLER ONE
                "matched_user_first_name": match.user2.first_name,
                "matched_user_last_name": match.user2.last_name,
                'content':message[0].content,
                'created_at':message[0].created_at,
            })
        else:
            match_with_no_msgs.append(match)

    # match1 = User.matches.through.objects.filter(from_user_id=newest_msg.author.id).filter(to_user_id=newest_msg.recipient.id)
    # match2 = User.matches.through.objects.filter(from_user_id=newest_msg.recipient.id).filter(to_user_id=newest_msg.author.id)
 


    # WHAT IF USER DOENST HAVE ANY MESSAGES YET
    # AND WHAT IF THEY DONT HAVE ANY MATCHES EITHER
    
    context = {
        'room_name': room_name,
        'user_id': request.session["user_id"],
        'first_name':User.objects.get(id=request.session["user_id"]).first_name,
        'last_name':User.objects.get(id=request.session["user_id"]).last_name,
        "matches": matches,
        "matched_user_id": matched_user.id,
        "matched_user_first_name":matched_user.first_name,
        'match_id': match_id,
        # "new_messages":new_messages,
        # 'match_with_no_msgs':match_with_no_msgs,
    }
    return render(request, 'chat/room.html', context)



# def ajax_message(request):

#     logged_user = User.objects.get(id=request.session["user_id"])

#     message = Message.objects.create(message=request.POST["message"], user=logged_user, match=Match.objects.get(id=1))

#     context = {
#         'all_messages' : logged_user.messages.all(),
#         "logged_user": logged_user,
#     }
#     return render(request, 'ajax_message.html',context)




# >>> matches = Match.objects.filter(user1 = 1).annotate(mcount = Count('messages')).order_by('-created_at')                   
# >>> matches
# <QuerySet [<Match: Match object (7)>, <Match: Match object (6)>, <Match: Match object (3)>, <Match: Match object (2)>]>
# >>> matches[0].mcount
# 10
# >>> messages = matches[0].messages.order_by('-created_at') 
# >>> messages[0]
# <Message: Dora>