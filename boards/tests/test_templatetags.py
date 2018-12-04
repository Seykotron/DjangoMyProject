from django import forms
from django.test import TestCase
from ..templatetags.form_tags import field_type, input_class

class ExampleForm(forms.Form):
    name = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        fields = ( "name", "password" )

# Pruebas para comprobar el tipo de los campos del formulario
class FieldTypeTests(TestCase):
    # Compruebo que los campos sean los correctos
    def test_field_widget_type(self):
        form = ExampleForm()
        self.assertEqual( "TextInput", field_type(form["name"]) )
        self.assertEqual( "PasswordInput", field_type(form["password"]) )

# Compruebo las clases que están en la etiqueta de input del formulario
class InputClassTests(TestCase):

    # Compruebo para los input que no están ligados
    def test_unbound_field_initial_state(self):
        form = ExampleForm()
        self.assertEqual("form-control ", input_class(form["name"]) )

    # Compruebo un input válido
    def test_valid_bound_field(self):
        form = ExampleForm( { "name":"john", "password" : "123" } )
        self.assertEqual( "form-control is-valid", input_class(form["name"]) )
        self.assertEqual( "form-control ", input_class(form["password"]) )

    # Compruebo un input inválido
    def test_invalid_bound_field(self):
        form = ExampleForm( { "name":"", "password" : "123" } )
        self.assertEqual( "form-control is-invalid", input_class(form["name"]) )
