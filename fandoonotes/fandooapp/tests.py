# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
from django.test import TestCase
from django.utils.decorators import method_decorator

from .models import Notes
from django.contrib.auth.models import User
from .decorators import api_login_required
from django.urls import reverse
from django.test.client import Client


# Testing the urls

class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('nilam', 'nilammore820@gmail.com', 'admin@1234')

    def testLogin(self):
        self.client.login(username='nilam', password='admin@1234')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    @method_decorator(api_login_required)
    def test_notes_api(self):
        # Issue a get request
        response = self.client.get('notes')
        # response = self.client.get(reverse('login'))
        # check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)


class SimpleTest(unittest.TestCase):
    def SetUp(self):
        # Every test needs a client
        self.client = Client()


# Testing the api


class EntryTest(TestCase):

    def test_details(self):
        # Issue a get request
        response = self.client.get('/login/')
        # check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Logout")

        # test case for login api

    def test_signup_form(self):
        # Issue a get request
        response = self.client.get('/signup/')
        # check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    # test case for S3bucket api
    def test_uploads3_api(self):
        # Issue a get request
        response = self.client.get('/upload/')
        # check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)



#
# class NotesTestCase(TestCase):
#     def setUp(self):
#         print("notes setup activity")
#         Notes.objects.create(title='test note1', discription='testcase note1', color='red', labels='testing')
#         Notes.objects.create(title='test note2', discription='testcase note2', color='pink', labels='testing')
#
#     @method_decorator(api_login_required)
#     def test_notes_info(self):
#         nl = Notes.objects.all()
#         self.assertEqual(nl.count(), 2)
#         # note1 = Notes.objects.get(name="test note1")
#         # note2 = Notes.objects.get(name="test note2")

#
# class Setup_Class(TestCase):
#
#     def setUp(self):
#         self.user = User.objects.create(username="nilam", password="admin@1234", email="nilammore820@gmail.com")
#
#
# class user_views_test(Setup_Class):
#     # Valid Data
#     def test_login_view(self):
#         user_login_data = self.client.user_login(username="nilam", password="admin@1234")
#         self.assertTrue(user_login_data)
#         response = self.client.get("/")
#         self.assertEqual(response.status_code, 302)
#
#     @method_decorator(api_login_required)
#     def test_noteslist_api(self):
#         # Issue a get request
#         response = self.client.get('/notes/')
#         # check that the response is 200 OK.
#         self.assertEqual(response.status_code, 200)
