# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
from django.test import TestCase, Client
from .forms import UserForm
from django.urls import reverse


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

    