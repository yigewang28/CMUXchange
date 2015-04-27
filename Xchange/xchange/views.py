from django.template import Template, RequestContext, loader
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.core.urlresolvers import reverse

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

from xchange.models import *

from django.utils import timezone
import datetime
from django.core import serializers
import json

from xchange.forms import *

from django.views.decorators.csrf import csrf_exempt

# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator

# Used to send mail from within Django
from django.core.mail import send_mail

# register view
@transaction.atomic
def register(request):
    context = {}
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'xchange/register.html', context)

    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'xchange/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password1'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'],
                                        email=form.cleaned_data['email'])
    new_user.is_active = False
    new_user.save()
    print(form.cleaned_data['email'])
    new_xchange_user = XchangeUser(user=new_user) 
    new_xchange_user.save()

    token = default_token_generator.make_token(new_user)
    email_body = """
Welcome to the CMU Xchange. Please click the link below to
verify your email address and complete the registration of your account:
  http://%s%s
""" % (request.get_host(), 
       reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message= email_body,
              from_email="yigew@andrew.cmu.edu",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']
    return render(request, 'xchange/needs-confirmation.html', context)

@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()
    return render(request, 'xchange/confirmed.html', {})

@login_required
def stream(request):
    items = Item.objects.all().order_by('-created')
    return render(request, 'xchange/stream.html', {'items' : items, \
                                                    'name' : request.user.username, \
                                                    'hasLogin' : 'true'})
@login_required
def books(request):
    items = Item.objects.filter(tag__contains="books").order_by('-created');
    return render(request, 'xchange/stream.html', {'items' : items, \
                                                    'name' : request.user.username, \
                                                    'hasLogin' : 'true'})

@login_required
def furnitures(request):
    items = Item.objects.filter(tag__contains="furnitures").order_by('-created');
    return render(request, 'xchange/stream.html', {'items' : items, \
                                                    'name' : request.user.username, \
                                                    'hasLogin' : 'true'})

@login_required
def electronics(request):
    items = Item.objects.filter(tag__contains="electronics").order_by('-created');
    return render(request, 'xchange/stream.html', {'items' : items, \
                                                    'name' : request.user.username, \
                                                    'hasLogin' : 'true'})

@login_required
def dorms(request):
    items = Item.objects.filter(tag__contains="dorms").order_by('-created');
    return render(request, 'xchange/stream.html', {'items' : items, \
                                                    'name' : request.user.username, \
                                                    'hasLogin' : 'true'})

@login_required
def others(request):
    items = Item.objects.filter(tag__contains="others").order_by('-created');
    return render(request, 'xchange/stream.html', {'items' : items, \
                                                    'name' : request.user.username, \
                                                    'hasLogin' : 'true'})
@login_required
def clothing(request):
    items = Item.objects.filter(tag__contains="clothing").order_by('-created');
    return render(request, 'xchange/stream.html', {'items' : items, \
                                                    'name' : request.user.username, \
                                                    'hasLogin' : 'true'})


def globalstream_json(request):
    items = Item.objects.all().order_by('-created')
    tempList = []
    for item in items:
        comments = item.comment_set.all().order_by('created')
        tempCommentList = []
        for comment in comments:
            tempCommentList.append({
                "created":str(comment.created), 
                "username":comment.xchangeuser.user.username, 
                "userid":comment.xchangeuser.user.id,
                "text":comment.text})
        tempList.append({"itemid":item.id, 
            "created":str(item.created), 
            "username":item.xchangeuser.user.username, 
            "userid":item.xchangeuser.user.id,
            "text":item.text,
            "itemprice":item.itemprice,
            "itemname":item.itemname,
            "comments":tempCommentList})
    # response_text = serializers.serialize('json',tempList)
    response_text = json.dumps(tempList) #dump list as JSON
    return HttpResponse(response_text, content_type='application/json')

@login_required
@transaction.atomic
def post(request):
    result_page = render(request, 'xchange/post.html')
    if request.POST:
        form = PostForm(request.POST, request.FILES);
        if not form.is_valid():
            result_page = render(request, 'xchange/post.html',{'name' : request.user.username, \
                                                                 'hasLogin' : 'true',\
                                                                 'inputErrors' : form.errors})
            return result_page
        new_item = Item(text=form.cleaned_data['content'],\
                        xchangeuser=request.user.xchangeuser,\
                        itemname=form.cleaned_data['itemname'],\
                        itemprice=form.cleaned_data['itemprice'],\
                        itemphoto=form.cleaned_data['itemphoto'],\
                        tag=form.cleaned_data['tag'],\
                        content_type=form.cleaned_data['itemphoto'].content_type)
        new_item.save()
        result_page = stream(request)
    else :
        result_page = render(request, 'xchange/post.html',{'name' : request.user.username, \
                                                                 'hasLogin' : 'true'})
    return result_page



def get_itemphoto(request, id):
    item = get_object_or_404(Item, id=id)
    print(item.itemphoto)
    if not item.itemphoto:
        raise Http404
    return HttpResponse(item.itemphoto, content_type=item.content_type)

@login_required
def profile(request, id):
    tempuser = get_object_or_404(User, id=id)
    hasfollow = "self"
    if not tempuser.username==request.user.username:
        hasfollow = "follow"
        myself = False
        if request.user.xchangeuser.followlist.all().filter(user__exact=tempuser):
            hasfollow = "unfollow"
    if tempuser.username==request.user.username:
        myself = True

    # items = Item.objects.filter(xchange_user=tempuser).order_by('-created'); 
    items = tempuser.xchangeuser.item_set.all().order_by('-created');
    return render(request, 'xchange/profile.html', {'user':tempuser, \
                                                          'items' : items, \
                                                          'hasLogin' : 'true', \
                                                          'hasfollow': hasfollow, \
                                                          'myself': myself})

@login_required
def myprofile(request):
    if request.method == 'GET':
        return redirect(reverse('profile', args=(request.user.id,)))
    else:
        raise Http404


@login_required
@transaction.atomic
def editprofile(request):
    context = {}
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        form = EditProfileForm(initial={'username':request.user.username,\
                                        'first_name':request.user.first_name, \
                                        'last_name': request.user.last_name, \
                                        'bio':request.user.xchangeuser.bio})
        context['form'] = form

        context['hasLogin'] = 'true'
        return render(request, 'xchange/editprofile.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    print request.FILES
    form = EditProfileForm(request.POST, request.FILES, user=request.user)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        context['hasLogin'] = 'true'
        context['errors'] = form.errors
        return render(request, 'xchange/editprofile.html', context)
    # At this point, the form data is valid.  Register and login the user.
    
    request.user.username = form.cleaned_data['username']
    request.user.last_name = form.cleaned_data['last_name']
    request.user.first_name = form.cleaned_data['first_name']
    request.user.save()

    tempXchangeUser = request.user.xchangeuser
    tempXchangeUser.content_type = form.cleaned_data['picture'].content_type
    tempXchangeUser.bio = form.cleaned_data['bio']
    tempXchangeUser.picture = form.cleaned_data['picture']
    tempXchangeUser.save()

    return redirect(reverse('xchange.views.profile', args=(request.user.id,)))

def get_photo(request, id):
    tempUser = get_object_or_404(User, id=id).xchangeuser
    if not tempUser.picture:
        raise Http404
    print tempUser.picture
    return HttpResponse(tempUser.picture, content_type=tempUser.content_type)

@login_required
@transaction.atomic
def follow(request, id):
    if request.POST:
        targetUser = get_object_or_404(User, id=id).xchangeuser
        currentUser = request.user.xchangeuser
        if not targetUser:
            raise Http404
        if currentUser.followlist.all().filter(user__exact=targetUser.user):
            raise Http404
        currentUser.followlist.add(targetUser)
        currentUser.save()
    return redirect(reverse('xchange.views.profile', args=(id,)))

@login_required
@transaction.atomic
def unfollow(request, id):
    if request.POST:
        targetUser = get_object_or_404(User, id=id).xchangeuser
        currentUser = request.user.xchangeuser
        if not currentUser.followlist.all().filter(user__exact=targetUser.user):
            raise Http404
        currentUser.followlist.remove(targetUser)
        currentUser.save()
    return redirect(reverse('xchange.views.profile', args=(id,)))

@login_required
def followstream(request):
    currentFollowList = request.user.xchangeuser.followlist.all();
    items = Item.objects.filter(xchangeuser__in=currentFollowList).order_by('-created')
    return render(request, 'xchange/followstream.html', {'user':request.user, \
                                                          'items' : items, \
                                                          'hasLogin' : 'true',})
@login_required
@transaction.atomic
def addcomment(request, id):
    #validate id 
    tempItem = get_object_or_404(Item, id=id)
    if request.POST:
        tempxchangeuser = request.user.xchangeuser
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = Comment(text=request.POST['content'],\
                            xchangeuser=request.user.xchangeuser,\
                            item=tempItem)
            new_comment.save()

    comments = tempItem.comment_set.all().order_by('created')
    tempList = []
    for comment in comments:
        tempList.append({
            "created":str(comment.created), 
            "username":comment.xchangeuser.user.username, 
            "userid":comment.xchangeuser.user.id,
            "text":comment.text})
    # response_text = serializers.serialize('json',tempList)
    response_text = json.dumps(tempList) #dump list as JSON
    return HttpResponse(response_text, content_type='application/json')


@login_required
@transaction.atomic
def search(request):
    if not 'searchitem' in request.POST:
        return render(request, 'xchange/searchstream.html', {'hasLogin': True})

    searchitem = request.POST['searchitem']
    print searchitem
    objects = Item.objects.filter(itemname__contains=searchitem).order_by('-created');
    print objects.count()
    if objects.count() == 0:
        message = 'Sorry. There is no item named "{0}"'.format(searchitem)
        return render(request, 'xchange/searchstream.html', {'message': message, 'hasLogin': True})


    context = { 'items': objects.all(), 'hasLogin': True }
    return render(request, 'xchange/searchstream.html', context)



@login_required
@transaction.atomic
def delete(request, id):
    if request.method != 'POST':
        message = 'Invalid request. POST method must be used.'
        return render(request, 'xchange/stream.html', { 'message': message })

    item = get_object_or_404(Item, id=id)
    print(item.id)
    print(item.itemname)
    item.delete()
    items = Item.objects.all().order_by('-created')
    context = { 'items': items, 'hasLogin': True}
    #message = '{0} has been deleted.'.format(item)
    tempuser = request.user
    hasfollow = "self"
    if not tempuser.username==request.user.username:
        hasfollow = "follow"
        myself = False
        if request.user.xchangeuser.followlist.all().filter(user__exact=tempuser):
            hasfollow = "unfollow"
    if tempuser.username==request.user.username:
        myself = True
    # items = Item.objects.filter(xchange_user=tempuser).order_by('-created'); 
    items = tempuser.xchangeuser.item_set.all().order_by('-created');
    return render(request, 'xchange/profile.html', {'user':tempuser, \
                                                          'items' : items, \
                                                          'hasLogin' : 'true', \
                                                          'hasfollow': hasfollow, \
                                                          'myself': myself})
    #return render(request, 'xchange/profile.html', context)



    


