import os
import unittest
import rt
import requesttracker
from errbot.backends.test import testbot
from errbot import plugin_manager

RT_CONFIG = {'USER': os.environ.get('RT_USER'),
             'PASSWORD': os.environ.get('RT_PASSWORD'),
             'DISPLAY_URL': os.environ.get('RT_DISPLAY_URL'),
             'REST_URL': os.environ.get('RT_REST_URL')}

BAD_PASSWORD = {'USER': os.environ.get('RT_USER'),
                'PASSWORD': 'badpassword',
                'DISPLAY_URL': os.environ.get('RT_DISPLAY_URL'),
                'REST_URL': os.environ.get('RT_REST_URL')}

BAD_URL = {'USER': os.environ.get('RT_USER'),
           'PASSWORD': 'badpassword',
           'DISPLAY_URL': os.environ.get('RT_DISPLAY_URL'),
           'REST_URL': 'http://foo.example.com'}


class TestRT(object):
    extra_plugin_dir = '.'

    def test_configuration(self, testbot):
        testbot.push_message('!plugin config RT ' + str(RT_CONFIG))
        assert 'Plugin configuration done.' in testbot.pop_message()

    def test_configuration_empty(self, testbot):
        testbot.push_message('!plugin config RT {}')
        expected = "Incorrect plugin configuration: missing config value: "\
            "REST_URL"
        assert expected in testbot.pop_message()

    def test_configuration_login(self, testbot):
        testbot.push_message('!plugin config RT ' + str(BAD_PASSWORD))
        expected = "Incorrect plugin configuration: Authentication failed"
        assert expected in testbot.pop_message()

    def test_configuration_url(self, testbot):
        testbot.push_message('!plugin config RT ' + str(BAD_URL))
        expected = "Incorrect plugin configuration: Cannot connect to RT as"\
            " %s:" % (BAD_URL['USER'])
        assert expected in testbot.pop_message()

    def test_find_ticket(self, testbot):
        test_subject = 'RT plugin for Errbot - automated test'
        test_requestor = 'foo@example.com'
        test_text = 'Testing https://github.com/alimac/err-request-tracker'

        testbot.push_message('!plugin config RT ' + str(RT_CONFIG))
        assert 'Plugin configuration done.' in testbot.pop_message()

        tracker = rt.Rt(RT_CONFIG['REST_URL'])
        tracker.login(RT_CONFIG['USER'], RT_CONFIG['PASSWORD'])

        try:
            ticket_id = tracker.create_ticket(Queue='General',
                                              Subject=test_subject,
                                              Requestors=test_requestor,
                                              Text=test_text)
            ticket = tracker.get_ticket(ticket_id)
        except Exception as e:
            raise Exception("Unable to create a test ticket: " + str(e))

        testbot.push_message(str(ticket_id))
        assert "%s (%s%s) in General from %s" % (
            test_subject,
            RT_CONFIG['DISPLAY_URL'],
            str(ticket_id),
            test_requestor) in testbot.pop_message()

        testbot.push_message(RT_CONFIG['DISPLAY_URL'] + str(ticket_id))
        assert "%s (%s%s) in General from %s" % (
            test_subject,
            RT_CONFIG['DISPLAY_URL'],
            str(ticket_id),
            test_requestor) in testbot.pop_message()

        testbot.push_message("need help with " + str(ticket_id))
        assert "%s (%s%s) in General from %s" % (
            test_subject,
            RT_CONFIG['DISPLAY_URL'],
            str(ticket_id),
            test_requestor) in testbot.pop_message()

    def test_find_nonexistent_ticket(self, testbot):

        testbot.push_message('!plugin config RT ' + str(RT_CONFIG))
        assert 'Plugin configuration done.' in testbot.pop_message()

        tracker = rt.Rt(RT_CONFIG['REST_URL'])
        tracker.login(RT_CONFIG['USER'], RT_CONFIG['PASSWORD'])

        testbot.push_message('999999999999999999999999999999999999999999999')
        expected = "Sorry, that ticket does not exist or I cannot access it."
        assert expected in testbot.pop_message()

    def test_non_rt_url(self, testbot):
        testbot.push_message('!plugin config RT ' + str(RT_CONFIG))
        assert 'Plugin configuration done.' in testbot.pop_message()

        testbot.push_message('http://example.com?id=123')

        try:
            testbot.pop_message(block=False)
        except:
            pass
