from django.core import mail
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test import TestCase

# Creo una clase para probar que el mail se envía correctamente
class PasswordResetMailTests(TestCase):

    # Configuro el testcase
    def setUp(self):
        User.objects.create_user( username="john", email="john@doe.com", password="123" )
        self.response = self.client.post( reverse("password_reset"), { "email" : "john@doe.com" } )
        self.email = mail.outbox[0]

    # Compruebo el titulo del email
    def test_email_subject(self):
        self.assertEqual( "[Django Boards] Reinicio de contraseña", self.email.subject )

    # Compruebo el cuerpo del email
    def test_email_body(self):
        context = self.response.context
        token = context.get("token")
        uid = context.get("uid")
        password_reset_token_url = reverse(
            "password_reset_confirm",
            kwargs={
                "uidb64" : uid,
                "token" : token
            }
        )
        self.assertIn( password_reset_token_url, self.email.body )
        self.assertIn( "john", self.email.body )
        self.assertIn( "john@doe.com", self.email.body )

    # Compruebo que el email se ha enviado a quien debía enviarse
    def test_email_to(self):
        self.assertEqual( ["john@doe.com"], self.email.to )
