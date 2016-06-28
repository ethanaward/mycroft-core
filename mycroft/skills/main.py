# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.


import json
import requests
from os.path import expanduser, exists
from threading import Thread

from mycroft.configuration import ConfigurationManager
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.skills.core import load_skills, THIRD_PARTY_SKILLS_DIR
from mycroft.util.log import getLogger
from mycroft.pairing.client import DevicePairingClient
from mycroft.skills.wolfram_alpha import CerberusWolframAlphaClient

from mycroft.client.enclosure.api import EnclosureAPI

logger = getLogger("Skills")

__author__ = 'seanfitz'

client = None


def load_skills_callback():
    global client

    config = ConfigurationManager.get()
    config_core = config.get("core")
    cerberus = config_core.get('use_cerberus')

    if cerberus:
        try:
            CerberusWolframAlphaClient().query('test')
        except:
            pairing_client = DevicePairingClient()

            Thread(target=pairing_client.run).start()

            pairing_client.display_code(client)

            pairing_client._emit_paired(False, client)
            enclosure = EnclosureAPI(client)
            enclosure.activate_mouth_listeners(False)
            enclosure.mouth_text(pairing_client.pairing_code)

            while(not pairing_client.paired):
                pass

            enclosure.activate_mouth_listeners(True)

            pairing_client._emit_paired(True, client)

    load_skills(client)

    try:
        ini_third_party_skills_dir = expanduser(
            config_core.get("third_party_skills_dir"))
    except AttributeError as e:
        logger.warning(e.message)

    if exists(THIRD_PARTY_SKILLS_DIR):
        load_skills(client, THIRD_PARTY_SKILLS_DIR)

    if ini_third_party_skills_dir and exists(ini_third_party_skills_dir):
        load_skills(client, ini_third_party_skills_dir)


def connect():
    global client
    client.run_forever()


def main():
    global client
    client = WebsocketClient()

    def echo(message):
        try:
            _message = json.loads(message)

            if _message.get("message_type") == "registration":
                # do not log tokens from registration messages
                _message["metadata"]["token"] = None
            message = json.dumps(_message)
        except:
            pass
        logger.debug(message)

    client.on('message', echo)
    client.once('open', load_skills_callback)
    client.run_forever()


if __name__ == "__main__":
    main()
