from django import forms
from .models import Topic

class NewTopicForm(forms.ModelForm):
    my_default_errors = {
        'required': 'Este campo es obligatorio.',
        'invalid': 'No puede estar en blanco.'
    }
    message = forms.CharField(
                widget=forms.Textarea(
                    attrs={
                        "rows":5,
                        "placeholder" : "Qué estás pensando?"
                    }
                ),
                max_length=4000,
                help_text="Máximo 4.000 caracteres.",
                error_messages=my_default_errors
    )

    class Meta:
        model = Topic
        fields = ["subject", "message"]
