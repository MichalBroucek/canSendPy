

from src.eld_msg_group import ELD_msg_group


class ELD_simulation:
    """
    Simulation of Truck (J1939 messages) required for ELD project
    - Read and parse text file as source of simulation data
    - Simulate complete functionality for ELD:
            - vehicle speed:            CCVS (0xFEF1)
            - engine r.p.m.:            EEC1 (0xF004)
            - vehicle distance:         VHDR (0xFEC1)
            - engine hours response:    HOURS (0xFEE5)
            - VIN code response:        VI (0xFEEC)
    """

    def __init__(self, simulation_file):
        self.simulation_source_file = simulation_file
        self.msg_group_list = self.__get_msg_list()

    def __get_msg_list(self):
        """
        Get list of MSG group
        :return:
        """
        msg_list = []
        eld_msg_group = ELD_msg_group()
        with open(self.simulation_source_file, 'r') as sim_file:
            for line in sim_file:
                group_complete = False
                if line.startswith('#'):
                    eld_msg_group.description = self.__get_description(line)
                elif line.startswith('speed'):
                    # Normal line: parsing signal values for J1939 messages
                    eld_msg_group.vehicle_speed = self.__get_int_value_from_line(line, 'speed')
                    eld_msg_group.vehicle_distance = self.__get_int_value_from_line(line, 'distance')
                    eld_msg_group.engine_speed = self.__get_int_value_from_line(line, 'engine_rpm')
                    eld_msg_group.engine_hours = self.__get_engine_hours_from_line(line)
                elif line.startswith('duration'):
                    eld_msg_group.duration = self.__get_duration_from_line(line)
                    group_complete = True
                else:
                    print('Error: Unknown simulation line format: {0}'.format(line))

                if group_complete:
                    msg_list.append(eld_msg_group)
                    eld_msg_group = ELD_msg_group()
        return msg_list

    def print_simulation_sequence(self):
        """
        Print all msg group from msg group list
        :return:
        """
        print('-----------------------------------------------')
        for msg_group in self.msg_group_list:
            msg_group.print()
        print('-----------------------------------------------')

    def __get_description(self, line):
        """
        Get description from line
        :param line:
        :return:
        """
        description = line
        if description.startswith('#'):
            description = line[1:]
        return description.strip()

    def __get_duration_from_line(self, line):
        """
        Get duration from file as number of seconds
        :param line:
        :return:
        """
        # TODO: catch exceptions
        duration_str = line.split('=')[1]
        return int(duration_str)

    def __get_int_value_from_line(self, line, value):
        """
        Get speed or distance or engine_rpm value from line
        :param line: line to be parsed
        :param value:  value is speed | distance | engine_rpm
        :return:
        """
        # TODO: catch exceptions
        value_str = line.split(value)[1]
        if value_str.startswith('='):
            value_str = value_str[1:]
        value_str = value_str.split(';')[0]
        return int(value_str)

    def __get_engine_hours_from_line(self, line):
        """
        Get Engine hours from line as float number
        :param line:
        :return:
        """
        # TODO: catch exceptions
        hours_str = line.split('engine_hours')[1]
        if hours_str.startswith('='):
            hours_str = hours_str[1:]
        hours_str = hours_str.split(';')[0]
        return float(hours_str)
