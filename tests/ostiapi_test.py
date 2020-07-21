#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the example module."""
from os import getenv
from unittest import TestCase
import ostiapi


class TestOstiApi(TestCase):
    """Test the basic functionality."""

    username = getenv('OSTI_USERNAME', 'my-osti-account')
    password = getenv('OSTI_PASSWORD', 'my-osti-password')
    site_input_code = getenv('OSTI_SITE_CODE', 'my-osti-site-code')

    def setup_method(self, *_args, **kwargs):
        """Put the module into testing mode."""
        print("Turn ostiapi into test mode.")
        ostiapi.testmode()

    def _setup_reserve(self):
        """Setup an example reservation."""
        return ostiapi.reserve(
            {
                'title':'My upcoming dataset',
                'accession_num':'sample-ds-0001',
                'site_input_code': self.site_input_code
            },
            self.username,
            self.password
        )

    def test_reserve(self):
        """Test the reserve method in the ostiapi module."""
        data = self._setup_reserve()
        self.assertTrue('record' in data)
        self.assertTrue('title' in data['record'])
        self.assertEqual(data['record']['title'], 'My upcoming dataset')
        self.assertEqual(data['record']['status'], 'SUCCESS')
        self.assertEqual(data['record']['doi_status'], 'RESERVED')
        self.assertFalse(data['record']['status_message'], 'Status message should be none')

    def test_get(self):
        """Test the get method in the ostiapi module."""
        reserve_result = self._setup_reserve()
        data = ostiapi.get(
            reserve_result['record']['osti_id'],
            self.username,
            self.password
        )
        self.assertTrue('record' in data)
        self.assertTrue('title' in data['record'])
        self.assertEqual(data['record']['title'], 'My upcoming dataset')
        self.assertEqual(data['record']['doi_status'], 'PENDING')
        self.assertEqual(data['record']['accession_num'], 'sample-ds-0001')
