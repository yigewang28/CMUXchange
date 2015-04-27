from django.db import models
from django.utils.translation import gettext as _
import locale
from django.utils import timezone
import datetime
from dateutil.relativedelta import relativedelta
import pytz
from django import forms


from django.contrib.auth.models import User

class XchangeUser(models.Model):
	user = models.OneToOneField(User, primary_key=True)
	bio = models.CharField(max_length=430)
	followlist = models.ManyToManyField("self", blank=True, null=True)
	# picture = models.FileField(upload_to="pictures", blank=True)
	picture = models.FileField(upload_to = 'pictures', default='pictures/xchange.png')
	content_type = models.CharField(max_length=50) 

class Item(models.Model):
	itemname = models.CharField(max_length=50)
	itemprice = models.CharField(max_length=20)
	text = models.CharField(max_length=160)
	tag = models.CharField(max_length=50)
	xchangeuser = models.ForeignKey(XchangeUser)
	itemphoto = models.FileField(upload_to = 'items')
	content_type = models.CharField(max_length=50)
	created = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return self.text
	def save(self, *args, **kwargs):
		if not self.id:
			self.created = timezone.now()
		return super(Item, self).save(*args, **kwargs)

class Comment(models.Model):
	xchangeuser = models.ForeignKey(XchangeUser)
	created = models.DateTimeField(auto_now_add=True)
	text = models.CharField(max_length=280)
	item = models.ForeignKey(Item)
	def __unicode__(self):
		return self.text
	def save(self, *args, **kwargs):
		if not self.id:
			self.created = timezone.now()
		return super(Comment, self).save(*args, **kwargs)

