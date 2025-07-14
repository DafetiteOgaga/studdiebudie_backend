from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def defaultpage(request):
	"""
	Default page view that renders the default page template.
	"""
	return HttpResponse("Welcome to the Study Buddie Backend! This is the default page. Please navigate to the appropriate section using the provided links.")
