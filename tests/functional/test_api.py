# coding: utf-8
from __future__ import unicode_literals
import unittest
import sys
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'test_project.settings'

import six

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from pyuploadcare import conf
from pyuploadcare.api import rest_request, uploading_request,_build_user_agent
from pyuploadcare.exceptions import APIError, InvalidRequestError
from .utils import MockResponse


@patch.object(conf, 'secret', 'secret')
@patch('requests.sessions.Session.request', autospec=True)
class RESTClientTest(unittest.TestCase):
    def tearDown(self):
        conf.api_version = '0.5'

    def test_raises(self, request):
        request.return_value = MockResponse(404, b'{}')
        with self.assertRaises(InvalidRequestError):
            rest_request('GET', 'files/')

        request.return_value = MockResponse(200, b'meh')
        with self.assertRaises(APIError) as cm:
            rest_request('GET', 'files/')

        if sys.version_info >= (3, 4):
            self.assertEqual('Expecting value: line 1 column 1 (char 0)',
                             cm.exception.data)
        else:
            self.assertEqual('No JSON object could be decoded',
                             cm.exception.data)

    def test_request_headers(self, request):
        user_agent = _build_user_agent()

        request.return_value = MockResponse(200, b'[]')

        rest_request('GET', 'files/')
        headers = request.call_args[1]['headers']
        self.assertIn('Accept', headers)
        self.assertIn('User-Agent', headers)
        self.assertEqual(headers['Accept'],
                         'application/vnd.uploadcare-v0.5+json')
        self.assertEqual(headers['User-Agent'], user_agent)

        conf.api_version = '0.1'
        rest_request('GET', 'files/')
        headers = request.call_args[1]['headers']
        self.assertIn('Accept', headers)
        self.assertIn('User-Agent', headers)
        self.assertEqual(headers['Accept'],
                         'application/vnd.uploadcare-v0.1+json')
        self.assertEqual(headers['User-Agent'], user_agent)

    def test_head(self, request):
        request.return_value = MockResponse(200, b'')

        rest_request('HEAD', 'files/')

    def test_options(self, request):
        request.return_value = MockResponse(200, b'')

        rest_request('OPTIONS', 'files/')


@patch.object(conf, 'secret', 'secret')
@patch('requests.sessions.Session.request', autospec=True)
class SignatureTest(unittest.TestCase):
    def tearDown(self):
        conf.signed_uploads = False

    def test_signature_fields_added(self, request):
        conf.signed_uploads = True

        request.return_value = MockResponse(200, b'[]')

        uploading_request('GET', '')
        data = request.call_args[1]['data']
        self.assertIn('expire', data)
        self.assertIn('signature', data)

    def test_signature_fields_skipped(self, request):
        request.return_value = MockResponse(200, b'[]')

        uploading_request('GET', '')
        data = request.call_args[1]['data']
        self.assertNotIn('expire', data)
        self.assertNotIn('signature', data)
