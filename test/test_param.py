from unittest import TestCase
from unittest.mock import MagicMock

from src import param

__author__ = 'brouk'


class TestParam(TestCase):
    # preparing to test
    def setUp(self):
        """ Setting up for the test """
        self.param = param.Param()

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

    def test_parse_cmd_params_no_params(self):
        just_one_param = ["first_param_is_name_of_script", ]
        self.param.print_help = MagicMock()
        self.param.parse_cmd_params(just_one_param)
        self.param.print_help.assert_any_call()

    def test_parse_cmd_param_list_short(self):
        self.param.print_help = MagicMock()
        self.param.parse_interface_info_param = MagicMock()
        self.param.parse_cmd_params(["script_name", "-l", ])
        self.param.print_help.assert_not_called()
        self.param.parse_interface_info_param.assert_called_once_with(["-l", ])

    def test_parse_cmd_param_list_long(self):
        self.param.print_help = MagicMock()
        self.param.parse_interface_info_param = MagicMock()
        self.param.parse_cmd_params(["script_name", "--list", ])
        self.param.print_help.assert_not_called()
        self.param.parse_interface_info_param.assert_called_once_with(["--list", ])

    def test_parse_cmd_param_one_msg_short(self):
        self.param.print_help = MagicMock()
        self.param.parse_one_msg_param = MagicMock()
        self.param.parse_cmd_params(["script_name", "-s", "1", "2", "3", "4", "5", "6", "7", "8", "9", ])
        self.param.print_help.assert_not_called()
        self.param.parse_one_msg_param.assert_called_once_with(["-s", "1", "2", "3", "4", "5", "6", "7", "8", "9", ])

    def test_parse_cmd_param_one_msg_long(self):
        self.param.print_help = MagicMock()
        self.param.parse_one_msg_param = MagicMock()
        self.param.parse_cmd_params(
            ["script_name", "--send_one_message", "1", "2", "3", "4", "5", "6", "7", "8", "9", ])
        self.param.print_help.assert_not_called()
        self.param.parse_one_msg_param.assert_called_once_with(
            ["--send_one_message", "1", "2", "3", "4", "5", "6", "7", "8", "9", ])

    def test_parse_cmd_param_msg_multi_short(self):
        self.param.print_help = MagicMock()
        self.param.parse_multi_msg_param = MagicMock()
        self.param.parse_cmd_params(
            ["script_name", "-S", "10", "200", "1", "2", "3", "4", "5", "6", "7", "8", "9", ])
        self.param.print_help.assert_not_called()
        self.param.parse_multi_msg_param.assert_called_once_with(
            ["-S", "10", "200", "1", "2", "3", "4", "5", "6", "7", "8", "9", ])

    def test_parse_cmd_param_msg_multi_long(self):
        self.param.print_help = MagicMock()
        self.param.parse_multi_msg_param = MagicMock()
        self.param.parse_cmd_params(
            ["script_name", "--send_message_multi", "10", "200", "1", "2", "3", "4", "5", "6", "7", "8", "9", ])
        self.param.print_help.assert_not_called()
        self.param.parse_multi_msg_param.assert_called_once_with(
            ["--send_message_multi", "10", "200", "1", "2", "3", "4", "5", "6", "7", "8", "9", ])

    def test_parse_cmd_param_file_msg_short(self):
        self.param.print_help = MagicMock()
        self.param.parse_file_messages = MagicMock()
        self.param.parse_cmd_params(["script_name", "-f", "file_name", ])
        self.param.print_help.assert_not_called()
        self.param.parse_file_messages.assert_called_once_with(["-f", "file_name", ])

    def test_parse_cmd_param_file_msg_long(self):
        self.param.print_help = MagicMock()
        self.param.parse_file_messages = MagicMock()
        self.param.parse_cmd_params(["script_name", "--send_file_messages", "file_name", ])
        self.param.print_help.assert_not_called()
        self.param.parse_file_messages.assert_called_once_with(["--send_file_messages", "file_name", ])

    def test_parse_cmd_param_default_msg_short(self):
        self.param.print_help = MagicMock()
        self.param.parse_send_default_param = MagicMock()
        self.param.parse_cmd_params(["script_name", "-d", ])
        self.param.print_help.assert_not_called()
        self.param.parse_send_default_param.assert_called_once_with(["-d", ])

    def test_parse_cmd_param_default_msg_long(self):
        self.param.print_help = MagicMock()
        self.param.parse_send_default_param = MagicMock()
        self.param.parse_cmd_params(["script_name", "--send_default_messages", ])
        self.param.print_help.assert_not_called()
        self.param.parse_send_default_param.assert_called_once_with(["--send_default_messages", ])

    def test_parse_cmd_unknown_param(self):
        self.param.print_help = MagicMock()
        self.param.parse_cmd_params(["script_name", "-Z"])
        self.param.print_help.assert_any_call()

    def test_parse_cmd_unknown_params(self):
        self.param.print_help = MagicMock()
        self.param.parse_cmd_params(["script_name", "-Z", "Y"])
        self.param.print_help.assert_any_call()

    # TODO: add all valid parameters calls - for parsing argv

        # def test_get_msg_from_argv_list(self):
        #     self.fail()
        #
        # def test_get_msg_from_argvs(self):
        #     self.fail()
        #
        # def test_parse_one_msg_param(self):
        #     self.fail()
        #
        # def test_parse_multi_msg_param(self):
        #     self.fail()
        #
        # def test_parse_interface_info_param(self):
        #     self.fail()
        #
        # def test_parse_file_messages(self):
        #     self.fail()
        #
        # def test_parse_send_default_param(self):
        #     self.fail()
