from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from .models import Board

# Create your views here.

# Creo la clase Home
class Home(View):

    # Defino el parametro get
    def get(self, request):
        # Obtengo todos los boards
        boards = Board.objects.all()
        # Oldway!
        # return HttpResponse( response_html )
        return render( request, "home.html", {"boards" : boards } )
