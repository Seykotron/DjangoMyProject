from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import SignUpForm

# Create your views here.

# Creo la clase Signup
class Signup(View):

    # Defino el metodo get
    def get(self, request):
        form = SignUpForm()
        return render( request, "signup.html", {"form" : form} )

    # Defino el metodo POST
    def post(self, request):
        form = SignUpForm( request.POST )
        if form.is_valid():
            user = form.save()
            login( request, user )
            return redirect( "home" )
        return render( request, "signup.html", {"form": form} )
