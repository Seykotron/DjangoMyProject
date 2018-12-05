from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.views import View
from django.views.generic import UpdateView, ListView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import NewTopicForm, PostForm
from .models import Board, Topic, Post

# Creo la clase Home
class Home(ListView):
    model = Board
    context_object_name = "boards"
    template_name = "home.html"

# Creo la clase Board
# Codigo muerto que no se usa para saber como se hace sin la clase ListView
class BoardTopics(View):

    # Defino el metodo get
    def get(self, request, pk, *args, **kwargs):
        board =  get_object_or_404(Board, pk=pk)
        queryset = board.topics.order_by("-last_updated").annotate(replies=Count("posts") -1 )

        page = request.GET.get("page",1)
        paginator = Paginator( queryset, 20 )

        try:
            topics = paginator.page(page)
        except PageNotAnInteger:
            # Volvemos a la primera página
            topics = paginator.page(1)
        except EmptyPage:
            # Vamos a la ultima pagina
            topics = paginator.page( paginator.num_pages )

        return render( request, "topics.html", { "board": board, "topics" : topics } )

# Creo la clase TopicListView
class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset

# Creo la clase para manejar el posteo del nuevo topic
# El decorator acepta una lista y se aplica a la clase que se pasa por el atributo name
@method_decorator(login_required, name='dispatch')
class NewTopic(View):

    # Defino el metodo get
    def get(self, request, pk, *args, **kwargs):
        # Obtenemos el board
        board =  get_object_or_404(Board, pk=pk)
        # Obtenemos el usuario que crea el formulario
        form = NewTopicForm()
        return render( request, "new_topic.html", { "board": board, "form" : form } )

    # Defino el metodo post para manejar la inserccion de los datos
    def post(self, request, pk, *args, **kwargs):
        # Obtenemos el board
        board =  get_object_or_404(Board, pk=pk)
        # Obtenemos el usuario que crea el formulario
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect( 'topic_posts', pk=pk, topic_pk=topic.pk )
        return render( request, "new_topic.html", { "board" : board, "form" : form } )

# Creo la clase para ver los post de los topics
# Codigo muerto que no se usa para saber como se hace sin la clase ListView
class TopicPosts(ListView):

    # Defino el metodo get
    def get(self, request, pk, topic_pk, *args, **kwargs ):
        topic = get_object_or_404( Topic, board__pk=pk, pk=topic_pk )
        topic.views += 1
        topic.save()
        return render( request, "topic_posts.html", { "topic" : topic })

# Creo la clase para ver los post de los topics
class PostListView(ListView):
    model = Post
    context_object_name = "posts"
    template_name = "topic_posts.html"
    paginate_by = 2

    def get_context_data(self, **kwargs ):

        session_key = "viewed_topic_{}".format(self.topic.pk)
        if not self.request.session.get( session_key, False ):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True

        kwargs["topic"] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404( Topic, board__pk=self.kwargs.get("pk"), pk=self.kwargs.get("topic_pk") )
        queryset = self.topic.posts.order_by( "created_at" )
        return queryset

@method_decorator(login_required, name='dispatch')
class ReplyTopic(View):

    def get(self, request, pk, topic_pk, *args, **kwargs):
        topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
        form = PostForm()
        return render( request, "reply_topic.html", { "topic" : topic, "form" : form } )

    def post(self, request, pk, topic_pk, *args, **kwargs):
        topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
        form = PostForm( request.POST )
        if form.is_valid():
            post = form.save( commit=False )
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            topic_url = reverse( "topic_posts", kwargs={ "pk" : pk, "topic_pk" : topic_pk } )
            topic_post_url = "{url}?page={page}#{id}".format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            return redirect( topic_post_url )
        return render( request, "reply_topic.html", { "topic" : topic, "form" : form } )

@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ("message",)
    template_name = "edit_post.html"
    pk_url_kwarg = "post_pk"
    context_object_name = "post"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save( commit=False )
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect( "topic_posts", pk=post.topic.board.pk, topic_pk=post.topic.pk )
