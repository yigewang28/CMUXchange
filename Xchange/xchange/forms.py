from django import forms

from django.contrib.auth.models import User
from models import *
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

MAX_UPLOAD_SIZE= 250000000

class PostForm(forms.Form):
    content = forms.CharField(max_length=160,required=True)
    itemname = forms.CharField(max_length=160,required=True)
    itemprice = forms.DecimalField(max_digits=19, decimal_places=10, required=True)
    tag = forms.CharField(max_length=20,required=True)
    itemphoto = forms.FileField(label=_('itemphoto'), \
                                    required=False, \
                                    error_messages = {'invalid':_("Image files only")}, \
                                    widget=forms.FileInput)
    def clean(self):
        cleaned_data = super(PostForm, self).clean()
        return cleaned_data

    def clean_content(self):
        tempContent = self.cleaned_data.get('content')
        if not tempContent:
            raise forms.ValidationError("Invalid post content.")
        return tempContent

    def clean_itemphoto(self):
        picture = self.cleaned_data['itemphoto']
        if not picture:
            raise forms.ValidationError('No File is uploaded')
        if not hasattr(picture, 'content_type'):
            raise forms.ValidationError('No File is uploaded...')
        if not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(settings.MAX_UPLOAD_SIZE))
        return picture


class CommentForm(forms.Form):
    content = forms.CharField(max_length=160,required=True)

    def clean_content(self):
        tempContent = self.cleaned_data.get('content')
        if not tempContent:
            raise forms.ValidationError("Invalid post content.")
        return tempContent

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=20,required=True)
    last_name  = forms.CharField(max_length=20,required=True)
    username   = forms.CharField(max_length = 20,required=True)
    password1  = forms.CharField(max_length = 200, 
                                 label='Password', 
                                 widget = forms.PasswordInput(),
                                 required=True)
    password2  = forms.CharField(max_length = 200, 
                                 label='Confirm password',  
                                 widget = forms.PasswordInput(),
                                 required=True)
    email = forms.CharField(max_length = 75,required=True)
    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username

    def clean_email(self):
        temp = self.cleaned_data.get('email')
        cmuemail = str(temp)
        if not "cmu.edu" in cmuemail:
            raise forms.ValidationError("Please use your cmu email to register.")
        return temp


class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=20,required=True, label = mark_safe('<strong>First Name</strong>'))
    last_name = forms.CharField(max_length=20,required=True, label = mark_safe('<strong>Last Name</strong>'))
    username = forms.CharField(max_length=20,required=True, label = mark_safe('<strong>Username</strong>'))
    picture = forms.FileField(label = mark_safe('<strong>Avatar</strong>'), \
                                    required=False, \
                                    error_messages = {'invalid':_("Image files only")}, \
                                    widget=forms.FileInput)
    bio = forms.CharField(widget=forms.Textarea, label = mark_safe('<strong>About Me</strong>'))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EditProfileForm, self).__init__(*args, **kwargs) 
    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if username != self.user.username and User.objects.filter(username=username):
            raise forms.ValidationError("Username is already taken.")
        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username
    #def clean_age(self):
     #   age = self.cleaned_data.get('age')
     #   if not age:
    #        raise forms.ValidationError("Invalid age.")
    #    if age < 0:
    #        raise forms.ValidationError("Invalid age.")
     #   return age
    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture:
            raise forms.ValidationError('No File is uploaded')
        if not hasattr(picture, 'content_type'):
            raise forms.ValidationError('No File is uploaded')
        if not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(settings.MAX_UPLOAD_SIZE))
        return picture