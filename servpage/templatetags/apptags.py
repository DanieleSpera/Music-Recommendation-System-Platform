from django import template
from ftft.canzoni.models import *
from django.db.models import Count

register = template.Library()


@register.filter
def subtract(value, arg):
    return value - arg

@register.assignment_tag
def slotpergruppo(group, collection):
	return canzone.objects.filter(gruppo=group).filter(slotcanzoni=collection).count()

@register.filter
def startswith(value, arg):
    value = str(value)
    value=value.lower()
    return value.startswith(arg.lower());