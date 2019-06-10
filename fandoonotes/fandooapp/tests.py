# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.contrib.auth.models import User
from . forms import UserForm   # import all forms
# Create your tests here.


class Setup_Class(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="nilam", password="admin@1234", email="nilammore820@gmail.com")


class User_Form_Test(TestCase):

    # Valid Form Data
    def test_UserForm_valid(self):
        form = UserForm(data={'username': "nilam", 'password': "admin@1234", 'email': "nilammore820@gmail.com"})
        self.assertFalse(form.is_valid())

    # Invalid Form Data
    def test_UserForm_invalid(self):
        form = UserForm(data={'username': "mp", 'password': "mp", 'email': ""})
        self.assertFalse(form.is_valid())

# test cases for views


class User_Views_Test(Setup_Class):
    # Valid Data
    def test_login_view(self):
        user_login = self.client.login(username="nilam", password="admin@1234")
        self.assertTrue(user_login)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)

    def test_signup_view(self):
        response = self.client.get("signup")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Please confirm your email address to complete the registration")

    # Invalid Data
    def test_add_user_invalidform_view(self):
        response = self.client.post("include url to post the data given",
                                    {'username': "admin", 'password': "", 'email':"admin@gmail.com"})
        self.assertTrue('"error": true' in response.content)
