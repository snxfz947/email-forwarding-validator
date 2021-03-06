from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from lib.debugging import *
from lib.utils import *

import argparse


def setup_parser(parser):
    parser.add_argument("--clear", action="store_true", help="clear configuration including (...)")
    parser.add_argument("--python_invoker", help="command used to invoke Python - default is python3")


def setup_invoker(invoker):
    dev_config = config_get_dev()
    dev_config["python_invoker"] = invoker
    print_message("Setting Python invoker to " + invoker, "CONFIG", "info")
    with open("../dev_config.json", "w") as config_file:
        json.dump(dev_config, config_file, indent=4, sort_keys=True)


def clear_configuration():
    config_clear_user_config()
    config_clear_cronjob_repo_path()
    config_clear_receive_credentials()
    config_clear_send_credentials()
    config_delete_tokens()
    print_message("Configuration has been cleared!", "CONFIG", "info")


def create_token(token_path, credentials_path, scopes, parser):
    store = file.Storage(token_path)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(credentials_path, scopes)
        flags = parser.parse_args()
        creds = tools.run_flow(flow, store, flags)
        build('gmail', 'v1', http=creds.authorize(Http()))
        return True
    else:
        return False


def configure_cronjob():
    if config_replace_cronjob_line("{repo_path_cmd}", "repo_path=" + config_get_repo_path()):
        print_message("Cronjob configured", "CONFIG", "info")


def main():
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    setup_parser(parser)

    invoker = parser.parse_args().python_invoker

    if invoker:
        setup_invoker(invoker)
    elif parser.parse_args().clear:
        clear_configuration()
    else:
        configure_cronjob()

        res = create_token("../send/token.json", "../send/credentials-send.json", config_get_scopes()["send"], parser)
        if not res:
            print("Token for send already exists!")
        res = create_token("../receive/token.json", "../receive/credentials-receive.json", config_get_scopes()["receive"], parser)
        if not res:
            print("Token for receive already exists!")


if __name__ == '__main__':
    main()
