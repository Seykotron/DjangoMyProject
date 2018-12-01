from django.db import models
from django.contrib.auth.models import User

# Clase Board -> es el panel en el que salen los "topic"
class Board(models.Model):
    # El nombre es unico, es decir solo un board por nombre identico y maximo 30 caracteres
    name        = models.CharField(max_length=30, unique=True)
    # A la descripcion le damos algo mas de cancha
    description = models.CharField(max_length=100)

    # Este metodo devuelve la representacion en string del objeto
    def __str__(self):
        return self.name

# Clase Topic -> es el hilo sobre el que se escriben los comentarios
class Topic(models.Model):
    # El titulo tan solo tiene 255 caracteres como maximo
    subject         = models.CharField(max_length=255)
    # Es la fecha de la ultima actualizacion del hilo, y se pone a la fecha actual con la creacion del mismo
    last_updated    = models.DateTimeField(auto_now_add=True)
    # Se establece una relacion de clave foranea con el Board con el campo topics
    board           = models.ForeignKey( Board, related_name="topics", on_delete=models.CASCADE )
    # Se establece una relacion de clave foranea con el Usuario que creo el Topic con el campo topics
    starter         = models.ForeignKey( User, related_name="topics", on_delete=models.CASCADE )

    # Este metodo devuelve la representacion en string del objeto
    def __str__(self):
        return self.subject

# Clase Posts -> son los comentarios que se agregan a los hilos
class Post(models.Model):
    # Este es el mensaje que escribe el usuario, tiene como maximo 4 mil caracteres
    message         = models.TextField( max_length=4000 )
    # Se establece una relacion de clave foranea con los hilos con el campo posts
    topic           = models.ForeignKey( Topic, related_name="posts", on_delete=models.CASCADE )
    # Fecha en la que se crea el post
    created_at      = models.DateTimeField( auto_now_add=True )
    # Fecha de la ultima actualizacion del post
    updated_at      = models.DateTimeField( auto_now_add=True )
    # Usuario que creo el post
    created_by      = models.ForeignKey( User, related_name="posts", on_delete=models.CASCADE )
    # Usuario que actualizo el post, related_name="+" <-- significa que no deseamos una relación inversa para que django no la cree
    updated_by      = models.ForeignKey( User, null=True, related_name="+", on_delete=models.CASCADE )

    # Este metodo devuelve la representacion en string del objeto
    def __str__(self):
        return self.created_by.username
