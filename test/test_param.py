from unittest import TestCase

from src import helper

__author__ = 'brouk'


class TestParam(TestCase):

    # preparing to test
    def setUp(self):
        """ Setting up for the test """
        self.param = helper.Param()

    # ending the test
    def tearDown(self):
        """Cleaning up after the test"""
        self.param = None

    def test_default_init(self):
        self.assertIsNone(self.param.action, msg='action is "None" by default')
        self.assertIsNone(self.param.timeout, msg='timeout is "None" by default')
        self.assertIsNone(self.param.nmb_msgs, msg='nmb_msgs is "None" by default')
        self.assertIsNone(self.param.delay, msg='delay is "None" by default')
        self.assertIsNone(self.param.msg, msg='msg is "None" by default')
        self.assertIsNone(self.param.file_name, msg='file_name is "None" by default')

    def test_parse_cmd_params(self):
        just_one_parameter = ["first",]
        #self.param.parse_cmd_params(just_one_parameter)
        # mock ???
        self.fail()

    def test_print_help(self):
        self.fail()

    def test_get_msg_from_argv_list(self):
        self.fail()

    def test_get_msg_from_argvs(self):
        self.fail()

    def test_parse_one_msg_param(self):
        self.fail()

    def test_parse_multi_msg_param(self):
        self.fail()

    def test_parse_interface_info_param(self):
        self.fail()

    def test_parse_file_messages(self):
        self.fail()

    def test_parse_send_default_param(self):
        self.fail()
