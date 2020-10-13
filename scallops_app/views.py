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
from .forms import ProfileForm, UserForm, ImageForm
import json

def index(request):
    if "user_id" not in request.session:
        return redirect("/login/")
    print("logged user is: "+ str(request.session["user_id"]))
    
    request.session['num_matches'] = len(Match.objects.filter(user1=request.session["user_id"]))

    context = {
        "user" : User.objects.get(id=request.session["user_id"]),
        "all_users" : User.objects.exclude(id=request.session["user_id"]),
        "user_id" : request.session["user_id"],
    }
    return render(request,'base.html', context)

def display_about_us(request):
    if "user_id" not in request.session:
        return redirect("/login/")

    request.session['num_matches'] = len(Match.objects.filter(user1=request.session["user_id"]))
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
    request.session['num_matches'] = len(Match.objects.filter(user1=request.session["user_id"]))
    context = {
        "user" : User.objects.get(id=request.session["user_id"]),
        "all_users" : User.objects.exclude(id=request.session["user_id"]),
    }
    return render(request,'contact_us.html',context)
def display_registration(request):
    
    return render(request, 'registration.html')

def process_registration(request):
    errors = User.objects.user_validator(request.POST)

    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
            
        return redirect('/registration/')
    else:
        password = request.POST["password"]
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode() 
        user = User.objects.create(first_name=request.POST["first_name"], last_name=request.POST["last_name"], email=request.POST["email"], password=pw_hash, birthday = request.POST["birthday"], gender=request.POST["gender"], city = request.POST["city"])
        Profile.objects.create(user=user)
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
            request.session["user_last"] = logged_user.last_name
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

def display_profile(request):
    if "user_id" not in request.session:
        return redirect("/login/")
    request.session['num_matches'] = len(Match.objects.filter(user1=request.session["user_id"]))
    logged_user = User.objects.get(id=request.session["user_id"])
    context = {
        "user" : logged_user,
        "all_users" : User.objects.exclude(id=request.session["user_id"]),
        "profile": Profile.objects.get(user=logged_user),
    }
    return render(request, 'profile.html',context)

def display_1on1(request):
    if "user_id" not in request.session:
        return redirect("/login/")

    logged_user = User.objects.get(id=request.session["user_id"])
    request.session['num_matches'] = len(Match.objects.filter(user1=request.session["user_id"]))

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
   
    if "user_id" not in request.session:
        return redirect("/login/")
    logged_user = User.objects.get(id=request.session["user_id"])
    request.session['num_matches'] = len(Match.objects.filter(user1=request.session["user_id"]))
    profile = Profile.objects.get(user=logged_user)
    
    if request.method == "POST":
        if 'profile' in request.POST:
            profileForm = ProfileForm(request.POST or None, request.FILES, instance=profile )
            if profileForm.is_valid():
                profile = profileForm.save(commit= False)
                profile.save()
                messages.success(request, "You successfully updated your profile")
      
                return redirect("/profile")
            else:
                context= {
                'profileForm': profileForm,
                'profile':profile,
                'userForm': UserForm(None, instance = logged_user ),
                'imageForm':ImageForm(None, instance=profile),
                'error': 'The form was not updated successfully.'}
                return render(request,'account-settings.html' , context)
        
        elif 'image' in request.POST:
            imageForm = ImageForm(request.POST or None, request.FILES, instance=profile )
            if imageForm.is_valid():
                image = imageForm.save(commit= False)
                image.save()
                messages.success(request, "You successfully updated your image")
                return redirect("/profile")
            else:
                context= {
                'profileForm': ProfileForm(None, instance=profile),
                'userForm': UserForm(None, instance = logged_user ),
                'imageForm': imageForm,
                'profile':profile,
                'error': 'The image was not updated successfully.'}
                return render(request,'account-settings.html' , context)

        elif 'user' in request.POST:
            userForm = UserForm(request.POST or None, instance=logged_user)
            if userForm.is_valid():
                user = userForm.save(commit=False)
                user.save()
                messages.success(request, "You successfully updated user info")
                return redirect("/profile")
            else:
                context = {
                    'profileForm':ProfileForm(None, instance=profile),
                    'userForm': userForm,
                    'profile':profile,
                    'imageForm':ImageForm(None, instance=profile),
                    'error':'The form was not updated successfully',
                }
                return render(request, 'account-settings.html', context)

            
    else:
        profileForm = ProfileForm(None, instance= profile)
        userForm = UserForm(None, instance = logged_user )
        context= {
            'profileForm': profileForm,
            'userForm':userForm,
            'profile':profile,
            'imageForm':ImageForm(None, instance=profile),
        }
        return render(request, 'account-settings.html', context)


def process_profile(request):

    if request.method == 'POST' and request.FILES['image']:
        myfile = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

    
    user = User.objects.get(id=request.session["user_id"])
    profile = Profile.objects.get(user=user)
    quick = request.POST
    if profile:
        profile.update(image=uploaded_file_url,summary = quick['summary'], interest = quick['interest'], goals = quick['goals'])
    else:
        profile = Profile.objects.create(user = user, image=uploaded_file_url, summary = quick['summary'], interest = quick['interest'], goals = quick['goals'])
        print(profile)
    request.session['prof_id'] = profile.id
    context ={
         'uploaded_file_url' : uploaded_file_url,
         'user' : User.objects.get(id = request.session["user_id"]),
         'profile_info' : Profile.objects.get(id = request.session['prof_id']),
    }    
    return  render (request, 'profile.html', context)

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

    match = Match.objects.filter( Q(user1=logged_user.id, user2=matched_user.id) | Q(user1=matched_user.id, user2=logged_user.id)).order_by('id').all()[:1]
  
    return redirect ('/chat/'+ room_name + '/' + str(user_id) + '/' + str(match[0].id))



def room(request, room_name, user_id, match_id):
    if "user_id" not in request.session:
        return redirect("/login/")
    logged_user = User.objects.get(id=request.session['user_id'])
    request.session['num_matches'] = len(Match.objects.filter(user1=request.session["user_id"]))
    if logged_user.id != user_id:
        return redirect('/login')
    user1 = Match.objects.get(id=match_id).user1
    user2 = Match.objects.get(id=match_id).user2
    if user1 == logged_user:
        matched_user = user2
    else:
        matched_user = user1
    
    matches = Match.objects.filter(user1=user_id).annotate(message = Max('messages')).order_by('-message').all()[:30]
    user = User.objects.get(id=request.session["user_id"])

    context = {
        'room_name': room_name,
        'user_id': request.session["user_id"],
        'first_name':user.first_name,
        'last_name':user.last_name,
        'image': user.profile.image.url,
        "matched_user_id": matched_user.id,
        "matched_user_first_name":matched_user.first_name,
        'match_id': match_id,
        "match_image":matched_user.profile.image.url,
    }
    return render(request, 'chat/room.html', context)


def match_list(request):
    if "user_id" not in request.session:
        return redirect("/login/")
    matches = Match.objects.filter(user1=request.session["user_id"])
    request.session['num_matches'] = len(Match.objects.filter(user1=request.session["user_id"]))
    if not matches:
        return render(request, 'chatError.html')
    match_list = []
    for match in matches:
        if match.id > Match.objects.get(user1=match.user2.id, user2=request.session["user_id"]).id:
            matchId = Match.objects.get(user1=match.user2.id, user2=request.session["user_id"]).id
        else:
            matchId = match.id
        try:
            match_list.append({
                "id":matchId,
                "user2_id":match.user2.id,
                "first_name": match.user2.first_name,
                "last_name":match.user2.last_name,
                "birthday":match.user2.birthday,
                "gender":match.user2.gender,
                "city":match.user2.city,
                "summary":match.user2.profile.summary,
                "interest":match.user2.profile.interest,
                'image':match.user2.profile.image,
                'goals':match.user2.profile.goals,
            })
        except:
            match_list.append({
                "id":matchId,
                "user2_id":match.user2.id,
                "first_name": match.user2.first_name,
                "last_name":match.user2.last_name,
                "birthday":match.user2.birthday,
                "gender":match.user2.gender,
                "city":match.user2.city,
            })

    context = {
        'match_list' : match_list,
    }
    return render(request, "match_list.html", context)



