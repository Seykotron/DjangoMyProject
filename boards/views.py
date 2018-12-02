from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from .models import Board, Topic, Post
from django.contrib.auth.models import User
from .forms import NewTopicForm

# Create your views here.

# Creo la clase Home
class Home(View):

    # Defino el metodo get
    def get(self, request):
        # Obtengo todos los boards
        boards = Board.objects.all()
        # Oldway!
        # return HttpResponse( response_html )
        return render( request, "home.html", {"boards" : boards } )

# Creo la clase Board
class BoardTopics(View):

    # Defino el metodo get
    def get(self, request, pk, *args, **kwargs):
        board =  get_object_or_404(Board, pk=pk)
        return render( request, "topics.html", { "board": board } )

# Creo la clase para manejar el posteo del nuevo topic
class NewTopic(View):

    # Defino el metodo get
    def get(self, request, pk, *args, **kwargs):
        # Obtenemos el board
        board =  get_object_or_404(Board, pk=pk)
        # Obtenemos el usuario que crea el formulario
        # TODO: Cambiar por el usuario logueado
        user = User.objects.first()
        form = NewTopicForm()
        return render( request, "new_topic.html", { "board": board, "form" : form } )

    # Defino el metodo post para manejar la inserccion de los datos
    def post(self, request, pk, *args, **kwargs):
        # Obtenemos el board
        board =  get_object_or_404(Board, pk=pk)
        # Obtenemos el usuario que crea el formulario
        # TODO: Cambiar por el usuario logueado
        user = User.objects.first()
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = user
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=user
            )
            return redirect("board_topics", pk=board.pk) #TODO: redirect to the created topic page
        return render( request, "new_topic.html", { "board" : board, "form" : form } )
