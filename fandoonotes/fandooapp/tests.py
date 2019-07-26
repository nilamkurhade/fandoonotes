# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
from django.test import TestCase
from django.utils.decorators import method_decorator
from . models import Notes, Labels
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.client import Client


# Testing the urls

class LoginTestCase(unittest.TestCase):
    def setup(self):
        self.client = Client()
        self.user = User.objects.create_user('nilam', 'nilammore820@gmail.com', 'admin@1234')

    def test_login(self):
        self.client.login(username='nilam', password='admin@1234')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)


# testing models
class NoteModelTest(TestCase):

    def test_string_representation_for_notes_models(self):
        entry = Notes(title="test title")
        self.assertEqual(str(entry), entry.title)

    def test_string_representation_for_labels_models(self):
        entry = Labels(title="test title")
        self.assertEqual(str(entry), entry.title)


class ProjectTests(TestCase):

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class SimpleTest(unittest.TestCase):
    def setup(self):
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

    def test_notes(self):
        # Issue a get request
        response = self.client.get('/notes/')
        # check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_labels(self):
        # Issue a get request
        response = self.client.get('/labels/')
        # check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    