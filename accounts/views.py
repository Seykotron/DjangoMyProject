from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import UpdateView
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

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

@method_decorator(login_required, name="dispatch")
class UserUpdateView(UpdateView):
    model = User
    fields = ( "first_name", "last_name", "email" )
    template_name = "my_account.html"
    success_url = reverse_lazy( "my_account" )

    def get_object(self):
        return self.request.user
