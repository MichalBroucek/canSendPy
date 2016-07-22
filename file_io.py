"""
Helper methods to work with files
"""


class MsgGroup:
    """
    Class to hold group of messages with theirs delays
    """

    def __intit__(self):
        self.messages = []
        self.delay = 0

    def clean(self):
        """
        Reset object into the default state
        """
        self.messages = []
        self.delay = 0


def read_messages_from_file(file_name):
    """
    Read messages specified in text file and return list of list Messages with delays
    :param file_name: text file where all messages are specified
    :return: list of MsgGroup
    """
    file_lines = None
    with open(file_name) as f:
        file_lines = f.readlines()

    msg_group_list = []
    msg_group = MsgGroup()

    if file_lines is not None:
        for line in file_lines:
            if is_msg_line(line):
                msg_group.messages.append(get_msg_from_line(line))

            if is_delay_line(line):
                msg_group.delay = get_delay_from_line(line)
                file_lines.append(msg_group)
                msg_group.clean()

    return msg_group_list


def is_msg_line(line):
    """Check if string is message line"""
    if "delay" in line:
        return False
    else:
        return True


def is_delay_line(line):
    """Check if string is delay line"""
    if "delay" in line:
        return True
    else:
        return False


def get_msg_from_line(line):
    """
    Get message from message string
    :param line: which contains message definition
    :return: can.Message
    """
    pass


def get_delay_from_line(line):
    """
    Get delay from delay string
    :param line: which contains delay value in ms
    :return: delay
    """
    pass
