from mycroft.pairing.client import DevicePairingClient
import unittest
from os.path import dirname, join, abspath
from test.skills.core import MockEmitter
from mycroft.util.log import getLogger

__author__ = 'eward'
logger = getLogger(__name__)


class DevicePairingClientTest(unittest.TestCase):
    emitter = MockEmitter()
    client = DevicePairingClient()

    def check_emitter(self, type_list, result_list, keys):
        self.check_types(type_list)
        self.check_results(result_list, keys)
        self.emitter.reset()

    def check_types(self, type_list):
        for result in type_list:
            self.assertTrue(result in self.emitter.get_types())

    def check_results(self, result_list, keys):
        results = []
        for result in self.emitter.get_results():
            for key in keys:
                if key in result:
                    results.append(result[key])
        for value in results:
            self.assertTrue(value in result_list)

    def add_lines_from_file(self, filename, dialog_list):
        with open(abspath(join(dirname(__file__),
                               '../../mycroft/pairing/dialog', filename)),
                  'r') as dialog_file:
            for line in dialog_file.readlines():
                line = line.strip().replace('{{pairing_code}}',
                                            ', ,'.join(
                                                self.client.pairing_code))
                dialog_list.append(line)

    def test_send_enclosure_signals_false(self):
        self.client.send_enclosure_signals(self.emitter, False)
        self.check_emitter(['enclosure.mouth.listeners',
                            'enclosure.mouth.text'],
                           [self.client.pairing_code, False],
                           ['active', 'text'])

    def test_send_enclosure_signals_true(self):
        self.client.send_enclosure_signals(self.emitter, True)
        self.check_emitter(['enclosure.mouth.listeners'], [True], ['active'])

    def test_speak_not_paired_dialog(self):
        self.client.speak_not_paired_dialog(self.emitter)
        line_list = []
        self.add_lines_from_file('not.paired.dialog', line_list)
        self.add_lines_from_file('pairing.instructions.dialog', line_list)
        self.check_emitter(['speak'], line_list, ['utterance'])

    def test_speak_paired_dialog(self):
        self.client.speak_paired_dialog(self.emitter)
        line_list = []
        self.add_lines_from_file('paired.dialog', line_list)
        self.check_emitter(['speak'], line_list, ['utterance'])
