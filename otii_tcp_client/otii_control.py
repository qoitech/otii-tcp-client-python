#!/usr/bin/env python3
import argparse
import sys
from otii_tcp_client import otii_connection, otii as otii_application

def login(otii, username, password):
    otii.login(username, password)

def logout(otii):
    otii.logout()

def list_licenses(otii):
    licenses = otii.get_licenses()
    print(f'{"  Id"} {"Type":12} {"Reserved to":15} Hostname')
    for license in licenses:
        print(f'{license["id"]:4d} {license["type"]:12} {license["reservedTo"]:15} {license["hostname"]}')

def reserve_license(otii, id):
    otii.reserve_license(id)

def return_license(otii, id):
    otii.return_license(id)

def main():
    parser = argparse.ArgumentParser(description='Otii Control')
    subparsers = parser.add_subparsers(dest='command', title='commands', required=True)

    login_parser = subparsers.add_parser('login', help='Log in to Qoitech server')
    login_parser.add_argument('-u', '--username', dest='username', required=True, help='Username')
    login_parser.add_argument('-p', '--password', dest='password', required=True, help='Password')
    subparsers.add_parser('logout', help='Log out from Qoitech server')
    subparsers.add_parser('list-licenses', help='List all available licenses')
    reserve_parser = subparsers.add_parser('reserve-license', help='Reserve license')
    reserve_parser.add_argument('-i', '--id', dest='id', required=True, help='License id')
    return_parser = subparsers.add_parser('return-license', help='Return license')
    return_parser.add_argument('-i', '--id', dest='id', required=True, help='License id')
    args = parser.parse_args()
    command = args.command

    connection = otii_connection.OtiiConnection('localhost', 1905)
    connect_response = connection.connect_to_server()
    if connect_response["type"] == "error":
        print("Exit! Error code: " + connect_response["errorcode"] + ", Description: " + connect_response["payload"]["message"])
        sys.exit()
    otii = otii_application.Otii(connection)

    if command == 'login':
        login(otii, args.username, args.password)
    elif command == 'logout':
        logout(otii)
    elif command == 'list-licenses':
        list_licenses(otii)
    elif command == 'reserve-license':
        reserve_license(otii, int(args.id))
    elif command == 'return-license':
        return_license(otii, int(args.id))
    else:
        print(f'Unknown command {command}')

    connection.close_connection()

if __name__ == '__main__':
    main()
