import json
import os
from time import sleep

class StatisticsSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.full_statistics = False
            cls._instance.instrumentation_duration = 0.0
            cls._instance.create_monitor_duration = 0.0
            cls._instance.test_duration = 0.0
            cls._instance.full_statistics_dict = {}  # to monitor and events
            cls._instance.violations_dict = {}  # only to violations
            cls._instance.file_name = None
            cls._instance.current_test = None
        return cls._instance

    def print_statistics(self):
        """
        Print or save both monitor and violation statistics.
        """

        print("Generating statistics...")
        sleep(0.1)
        self._print_statistics_time()
        self._print_statistics_monitor_and_events()
        self._print_statistics_violations()

    def print_raw_statistics(self):
        """
        Print or save the time statistics of the raw tests
        """

        print("Generating statistics...")
        sleep(0.1)
        self._print_raw_statistics_time()

    def _print_raw_statistics_time(self):
        """
        Print the raw tool time measurements
        """
        print_msg = f"========================= Raw Time Measurements =========================\n"

        # Print out the elapsed time for raw tests
        print_msg += f"Time taken for running tests: {self.test_duration:.5f} seconds"

        if self.file_name:
            basename, ext = os.path.splitext(self.file_name)
            new_file_name = basename + '-time' + ext
            dict_message = {'test_duration': self.test_duration}
            self._save_in_file(new_file_name, print_msg, dict_message)
            print(f"Time measurements are saved in {new_file_name}.")
        else:
            print(print_msg)

    def _print_statistics_time(self):
        """
        Print the tool time measurements
        """
        print_msg = f"=========================== Time Measurements ===========================\n"

        # Print out the elapsed time for importing specs and instrumentation.
        print_msg += f"Time taken for instrumentation: {self.instrumentation_duration:.5f} seconds\n"
        print_msg += f"Time taken for creating monitors: {self.create_monitor_duration:.5f} seconds\n"
        print_msg += f"Time taken for running tests: {self.test_duration:.5f} seconds"

        if self.file_name:
            basename, ext = os.path.splitext(self.file_name)
            new_file_name = basename + '-time' + ext
            dict_message = {'instrumentation_duration': self.instrumentation_duration,
                            'create_monitor_duration': self.create_monitor_duration,
                            'test_duration': self.test_duration}
            self._save_in_file(new_file_name, print_msg, dict_message)
            print(f"Time measurements are saved in {new_file_name}.")
        else:
            print(print_msg)

    def _print_statistics_violations(self):
        """
        Print or save violation statistics.
        """
        print_msg = f"============================== Violations ==============================\n"
        total = 0
        for spec_name in self.violations_dict.keys():
            num = len(self.violations_dict[spec_name])
            total += num
            print_msg += f"Spec - {spec_name}: {num} violations\n"

        print_msg += f"Total Violations: {total} violations\n"
        print_msg += f"------------\n"
        for spec_name in self.violations_dict.keys():
            print_msg += f"Spec - {spec_name}:\n"
            for violation_info in self.violations_dict[spec_name]:
                violation = violation_info['violation']
                test_info = violation_info['test']
                print_msg += f"    {violation}, (Test: {test_info})\n"
            print_msg += f"------------\n"

        if self.file_name:
            basename, ext = os.path.splitext(self.file_name)
            new_file_name = basename + '-violations' + ext
            self._save_in_file(new_file_name, print_msg, self.violations_dict)
            print(f"Violations are saved in {new_file_name}.")
        else:
            print(print_msg)

    def _print_statistics_monitor_and_events(self):
        """
        Print or save monitor and events statistics.
        """
        if self.full_statistics:
            print_msg = (f"============================== Monitors and Events calls "
                         f"==============================\n")
            total = 0
            for spec_name in self.full_statistics_dict.keys():
                num = self.full_statistics_dict[spec_name]['monitors']
                total += num
                print_msg += f"Spec - {spec_name}: {num} monitors\n"
            print_msg += f"Total Monitors: {total} monitors\n"
            print_msg += f"------------\n"
            for spec_name in self.full_statistics_dict.keys():
                print_msg += f"Spec - {spec_name}:\n"
                for event in self.full_statistics_dict[spec_name]['events']:
                    num = self.full_statistics_dict[spec_name]['events'][event]
                    print_msg += f"    {event}: {num} times\n"
                print_msg += f"------------\n"

            if self.file_name:
                basename, ext = os.path.splitext(self.file_name)
                new_file_name = basename + '-full' + ext
                self._save_in_file(new_file_name, print_msg, self.full_statistics_dict)
                print(f"Full statistics are saved in {new_file_name}.")
            else:
                print(print_msg)
    def _save_in_file(self, new_file_name, print_msg, message_dict):
        with open(new_file_name, 'w') as f:
            if self.file_name.endswith('.json'):
                json.dump(message_dict, f, indent=2, default=str)
            else:
                f.write(print_msg)

    def add_instrumentation_duration(self, instrumentation_duration):
        """
        Update instrumentation duration statistics.
        """
        self.instrumentation_duration = instrumentation_duration

    def add_create_monitor_duration(self, create_monitor_duration):
        """
        Update import duration statistics.
        """
        self.create_monitor_duration = create_monitor_duration

    def add_test_duration(self, test_duration):
        """
        Update instrumentation duration statistics.
        """
        self.test_duration = test_duration

    def add_monitor_creation(self, spec_name):
        """
        Add monitor creation to statistics count.
        """
        if self.full_statistics:
            if spec_name not in self.full_statistics_dict:
                self.full_statistics_dict[spec_name] = {'monitors': 0, 'events': {}}
            self.full_statistics_dict[spec_name]['monitors'] += 1

    def add_violation(self, spec_name, violation):
        """
        Add violation to statistics with associated current test information.
        """
        if spec_name not in self.violations_dict:
            self.violations_dict[spec_name] = []

        violation_info = {'violation': violation, 'test': self.current_test}
        self.violations_dict[spec_name].append(violation_info)

    def add_events(self, spec_name, event_name):
        """
        Add event to statistics.
        """
        if self.full_statistics:
            if spec_name not in self.full_statistics_dict:
                self.full_statistics_dict[spec_name] = {'monitors': 0, 'events': {}}
            if event_name not in self.full_statistics_dict[spec_name]['events']:
                self.full_statistics_dict[spec_name]['events'][event_name] = 0
            self.full_statistics_dict[spec_name]['events'][event_name] += 1
    def set_current_test(self, test_name):
        """
        Add current test name and location to statistics.
        """
        self.current_test  = test_name

    def set_full_statistics(self):
        """
        Set the statistics to be full.
        It will print out all the
        violations and the monitors count.
        """
        self.full_statistics = True

    def set_file_name(self, file_name):
        """
        Set the file name for saving the statistics.
        """
        self.file_name = file_name