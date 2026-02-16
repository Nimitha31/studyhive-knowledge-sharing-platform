from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.db.models import Q
from .models import Room,Topic,Message,User
from .forms import RoomForm,UserForm,MyUserCreationForm


def home(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''

    rooms=Room.objects.filter(
          Q(topic__name__icontains=q) |
          Q(name__icontains=q) |
          Q(description__icontains=q)
          )

    topics=Topic.objects.all()[0:5]
    room_count=rooms.count()
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))
    context={"rooms":rooms,"topics":topics,"room_count":room_count,"room_messages":room_messages}
    return render(request,'base/home.html',context)

def room(request,pk):
        room=Room.objects.get(id=pk)
        room_messages=room.message_set.all()
        participants=room.participants.all()

        if request.method == 'POST':
            message=Message.objects.create(
                  user=request.user,
                  room=room,
                  body=request.POST.get('body') ,
                  file=request.FILES.get('file')    
            )
            room.participants.add(request.user)
            return redirect('room',pk=room.id)
        context={"room":room,"room_messages":room_messages,"participants":participants}
        return render(request,'base/room.html',context)

@login_required(login_url="login")
def createroom(request):
      form=RoomForm()
      topics=Topic.objects.all()
      if request.method=="POST":
            topic_name=request.POST.get('topic')
            topic,created=Topic.objects.get_or_create(name=topic_name)
            Room.objects.create(
                  host=request.user,
                  topic=topic,
                  name=request.POST.get('name'),
                  description=request.POST.get('description'),
        )
            return redirect('home')
      context={"form":form,"topics":topics}
      return render(request,'base/room_form.html',context)

@login_required(login_url="login")
def updateroom(request,pk):
      room=Room.objects.get(id=pk)
      topics=Topic.objects.all()
      form=RoomForm(instance=room)
      if request.user != room.host:
            return HttpResponse("You're not allowed here!")
      if request.method=="POST":
            topic_name = request.POST.get('topic')
            topic, created = Topic.objects.get_or_create(name=topic_name)
            room.name = request.POST.get('name')
            room.topic = topic
            room.description = request.POST.get('description')
            room.save()
            return redirect('home')
      context={"form":form,"topics":topics}
      return render(request,'base/room_form.html',context)

@login_required(login_url="login")
def deleteroom(request,pk):
      room=Room.objects.get(id=pk)
      if request.method=="POST":
            room.delete()
            return redirect('home')
      context={"obj":room}
      return render(request,'base/delete.html',context)

def loginpage(request):
      page='login'
      if request.user.is_authenticated:
            return redirect('home')
      if request.method=="POST":
            email=request.POST.get('email').lower()
            password=request.POST.get('password')

            try:
                  user=User.objects.get(email=email)
            except:
                  messages.error(request,'Username does not exist')
            user=authenticate(request,email=email,password=password)
            if user is not None:
                  login(request,user)
                  return redirect('home')
            else:
                  messages.error(request,'Username or password does not exist')
      context={'page':page}
      return render(request,'base/login_register.html',context)
def logoutuser(request):
      logout(request)
      return redirect('home')
def registeruser(request):
      form= MyUserCreationForm()
      if request.method == 'POST':
            form=MyUserCreationForm(request.POST)
            if form.is_valid():
                  user=form.save(commit=False)
                  user.username=user.username.lower()
                  user.save()
                  login(request,user)
                  return redirect('home')
            else:
                  messages.error(request,"An error Occured during registration")
      context={'form':form}
      return render(request,'base/login_register.html',context)

@login_required(login_url="login")
def deletemessage(request,pk):
      message=Message.objects.get(id=pk)
      if request.user != message.user:
            return HttpResponse("your not allowed here!")
      if request.method == 'POST':
            message.delete()
            return redirect('home')
      context={"obj":message}
      return render(request,'base/delete.html',context)


def userprofile(request,pk):
      user=User.objects.get(id=pk)
      rooms=user.room_set.all()
      room_messages=user.message_set.all()
      topic=Topic.objects.all()
      context={'user':user,'rooms':rooms,'room_messages':room_messages,"topic":topic}
      return render(request,'base/profile.html',context)

@login_required(login_url="login")
def updateuser(request):
      user=request.user
      form=UserForm(instance=user)
      if request.method == 'POST':
        form = UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
      context={"form":form}
      return render(request,'base/update_user.html',context)

def topicpage(request):
      q=request.GET.get('q') if request.GET.get('q') != None else ''
      topics = Topic.objects.filter(name__icontains=q)
      context={"topics":topics}
      return render(request,'base/topics.html',context)

def activitypage(request):
    room_messages = Message.objects.all()
    context={'room_messages': room_messages}
    return render(request, 'base/activity.html',context)