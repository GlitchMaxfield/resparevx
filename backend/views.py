from datetime import datetime
from decimal import Decimal
from email.policy import HTTP
import re
from unicodedata import name
from django.shortcuts import render,redirect
from django.shortcuts import reverse
from django.http import HttpResponse
from backend import models
from backend.models import Reaction, Topic, Choice,Comment
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from backend.forms import CommentForm
from datetime import datetime

# Create your views here.
def home(request):
    recommended=Topic.objects.all()[:20]
    trending=Topic.objects.all()[20:]
    slide=trending[:5]
    return render(request,'index.html',{'name':'Aravind','recommended':list(recommended),'trending':list(trending),'slide':slide})

def register(request):

    if request.method == "POST":        
      
      fname = request.POST['fname']
      lname = request.POST['lname']
      uname = request.POST['uname']
      email = request.POST['email']
      pass1 = request.POST['pass1']
      pass2 = request.POST['pass2']
      

      myuser = User.objects.create_user(uname, email, pass1)
      myuser.first_name=fname
      myuser.last_name=lname

      myuser.save()

      messages.success(request, "Your account has been successfully created")

      return redirect('signin')

    
    return render(request,"register.html")


def signin(request):
    if request.method == 'POST':
        uname = request.POST['uname']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=uname, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            # messages.success(request, "Logged In Sucessfully!!")
            return render(request, "index.html",{"fname":fname})
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('home')
    
    return render(request, "signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')

def topic(request,pk):
    topic=Topic.objects.get(id=pk)
    reactions=Choice.objects.filter(topic_id=pk)

    return render(request,'topic.html',{'topic':topic,'reactions':list(reactions),'percent':None})
    

def react(request,pk):
    if request.user.is_authenticated:
        user=request.user
        choice_id=int(request.POST['select'])
        choice=Choice.objects.get(id=choice_id)
        if Reaction.objects.filter(user_id=user).filter(topic_id=choice.topic_id).exists():
            reaction=Reaction.objects.filter(user_id=user).get(topic_id=choice.topic_id)
            old_choice=Choice.objects.get(id=reaction.choice_id)
            if old_choice.count >0:
                old_choice.count-=1
            else:
                old_choice.count=0
            old_choice.save()

            new_choice=Choice.objects.get(id=choice_id)
            new_choice.count+=1
            new_choice.save()
            reaction.choice_id=choice_id
            reaction.time=datetime.now()
            reaction.save()
        else:
            reaction=Reaction(time=datetime.now(),choice_id=choice_id,user_id=user.id,topic_id=choice.topic_id)
            reaction.save()
            
    else:
        return redirect('signin')
    messages.info(request,"Thank You")
    topic=Topic.objects.get(id=pk)
    choices=Choice.objects.filter(topic_id=pk)
    total_reactions=100/Decimal(Reaction.objects.filter(topic_id=pk).count())
    return render(request,'topic.html',{'topic':topic,'reactions':list(choices),'message':messages,'percent':total_reactions})
    #url='/topic/'+str(choice.topic_id)  
    #return redirect(url)
    #return redirect('request.META['HTTP_REFERER']')

def addcomment(request,pk):
    topic= Topic.objects.get(id=pk)

    form=CommentForm(instance=topic)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=topic)
        if form.is_valid():
            name = request.user.username
            body= form.cleaned_data['body'];

            c=Comment(topic=topic,name=name,body=body,date_added=datetime.now())
            c.save()
            return render(request,'topic.html',{'topic':topic,})
            #return redirect('topic')
        else:
            print('form is invalid')
    else:
        form=CommentForm()


    context= {
        'topic':topic,   
        'form':form
    }
    
    return render(request,'add_comment.html',context)


def search(request):
    search=request.GET['search']
    #topic= Topic.objects.all()
    topic= Topic.objects.filter(title__icontains=search)
    params = {'topic':topic}
    return render(request,'search.html',params)
    #return HttpResponse('I am search')    
