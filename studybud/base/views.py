from django.shortcuts import redirect, render
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Room, Topic, Message
from .forms import RoomForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
# rooms = [
#     {'id': 1, 'name':'lets learn python'},
#     {'id': 2, 'name':'design with me'},
#     {'id': 3, 'name':'frontend developers'},

# #      '1': 'lets learn python',
# #     '2': 'design with me',
# #     '3': 'frontend developers',
# ]
def loginPage(request):

    page = 'login'
    
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username') ##.lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request , 'User does not exist')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request , 'Username or password does not exist')
    context={'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    # page = 'register'
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An erro occurred!')
    
    context = {'form': form}
    return render(request,'base/login_register.html',context )

def home(request):
    if request.GET.get('q')!=None:
        q = request.GET.get('q')
    else: q = ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains = q)|
        Q(name__icontains = q)|
        Q(description__icontains = q)
        )

    topics = Topic.objects.all()
    
    room_count = rooms.count()

    showMessages = Message.objects.filter(
        Q(room__topic__name__icontains = q)
    )




    context = {'rooms': rooms, 'topics':topics, 'room_count':room_count, 'showMessages':showMessages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
    showMessages = room.message_set.all()
    paticapants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk = room.id)
    context = {'room': room, 'showMessages':showMessages, 'paticapants':paticapants}
    #  another way 1 context =  room
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()

    showMessages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user':user, 'rooms':rooms,'showMessages':showMessages,'topics':topics}
    return render(request, 'base/profile.html',context)

@login_required(login_url = 'login')
def creatRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')
        
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url = 'login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You are not allowed!')
    
    if request.method=='POST':
        form = RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url = 'login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed!')

    if request.method == 'POST':
            room.delete()
            return redirect('home')
    
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url = 'login')
def deleteMessage(request, pk):
    messages = Message.objects.get(id=pk)

    if request.user != messages.user:
        return HttpResponse('You are not allowed!')

    if request.method == 'POST':
            messages.delete()
            return redirect('home')
    
    return render(request, 'base/delete.html', {'obj':messages})

