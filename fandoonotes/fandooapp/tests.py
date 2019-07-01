# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
from django.test import TestCase, Client
from .forms import UserForm
# Testing the urls


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
    def test_get_api_json(self):
        response = self.client.get('/login/', format='json')
        self.assertValidJsonResponse(response)

    def assertValidJsonResponse(self, response):
        pass

    # test case for signup api
    def test_signup_form(self):
        # Issue a get request
        response = self.client.get('/signup/')
        # check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_get_signup_api_json(self):
        response = self.client.get('/signup/', format='json')
        self.assertValidJsonResponse(response)

    # test case for S3bucket api
    def test_uploads3_api(self):
        # Issue a get request
        response = self.client.get('/upload/')
        # check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_get_s3upload_api_json(self):
        response = self.client.get('/upload/', format='json')
        self.assertValidJsonResponse(response)

    # test case for social login
    # test case for github login
    def test_social_github_login_api(self):
        # Issue a get request
        response = self.client.get('/oauth/login/github/')
        # check that the response is 302 found.
        self.assertEqual(response.status_code, 302)

    # test case for facebook login
    def test_social_facebook_api(self):
        # Issue a get request
        response = self.client.get('/oauth/login/facebook/')
        # check that the response is 302 found.
        self.assertEqual(response.status_code, 302)

    # test case for crude operations
    def test_notes_api(self):
        response = self.client.get('/notes/')
        self.assertEqual(response.status_code, 200)

    def test_get_notes_api_json(self):
        response = self.client.get('/notes/', format='json')
        self.assertValidJsonResponse(response)

    # test case for crude operations
    def test_labels_api(self):
        response = self.client.get('/labels/')
        self.assertEqual(response.status_code, 200)

    def test_get_labels_api_json(self):
        response = self.client.get('/labels/', format='json')
        self.assertValidJsonResponse(response)


# class ViewTestCase(TestCase):
#     """Test suite for the api views."""
#
#     def set_Up(self):
#         """Define the test client and other test variables."""
#         self.client = APIClient()
#         self.notes_list = {'name': 'Test Note'}
#         self.response = self.client.post(
#             reverse('notes'),
#             self.notes_list,
#             format="json")
#
#     def test_api_can_create_a_notes(self):
#         """Test the api has bucket creation capability."""
#         self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)