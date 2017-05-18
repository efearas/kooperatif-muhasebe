from django import template
from koopmuhasebe.util import *

register = template.Library()

@register.filter(name='addclass')
def addclass(value, arg):
	return value.as_widget(attrs={'class': arg})

@register.filter(name='addid')
def addid(value, arg):
	return value.as_widget(attrs={'id': arg})
	
@register.filter(name='addwidgets')
def addwidgets(value, arg):	
	dic = string_to_dictionary(arg,',',':')	
	return value.as_widget(attrs=dic)
	