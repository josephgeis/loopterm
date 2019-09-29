#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import base64
import pickle

import click
import requests
import colorama
from colorama import Fore, Style
from tabulate import tabulate

from .spinner import Spinner

colorama.init(autoreset=True)

home = os.environ.get("HOME")

config = {}
login_config = {}

try:
    config = pickle.load(open(f"{home}/.loopterm.conf", "rb"))
except Exception:
    pass

try:
    login_config = pickle.load(open(f"{home}/.loopterm.login", "rb"))
except:
    pass


@click.group()
def cli():
    pass


@cli.command()
def login():
    global home
    global config
    global login_config

    subdomain = click.prompt(
        f"{Fore.MAGENTA}Subdomain", default=config.get("host"))
    username = click.prompt(f"{Fore.MAGENTA}Username",
                            default=login_config.get("username"))
    password = click.prompt(
        f"{Fore.MAGENTA}Password", hide_input=True)

    config["host"] = subdomain
    pickle.dump(config, open(f"{home}/.loopterm.conf", "wb"))

    login_config = {}

    s = Spinner("Logging in to School Loop...")
    s.start()
    try:
        r = requests.get(f"https://{subdomain}/mapi/login",
                         params={"version": 3},
                         auth=requests.auth.HTTPBasicAuth(username, password))
    except Exception:
        s.stop()
        msg = f"{Fore.RED}{Style.BRIGHT}Fatal Error! {Fore.BLUE}{Style.NORMAL}Couldn't connect to server. Check your internet connection and the subdomain entered."
        click.echo(msg)
        sys.exit(1)
    s.stop()
    if r.status_code == 401:
        msg = f"{Fore.RED}{Style.BRIGHT}Login failed! {Fore.BLUE}Check your username and password."
        click.echo(msg)
    elif r.status_code == 200:
        details = r.json()
        if details["isParent"] == False:
            msg = f"{Fore.RED}{Style.BRIGHT}Login error! {Fore.BLUE}{Style.NORMAL}Parent accounts do not work with LoopTerm."
            click.echo(msg)
            sys.exit(1)
        else:
            msg = f"{Style.BRIGHT}{Fore.GREEN}Login success! {Fore.BLUE}{Style.NORMAL}You are logged in as {Fore.YELLOW}{details['fullName']} {Fore.BLUE}at {Fore.YELLOW}{details['students'][0]['school']['name']}{Fore.BLUE}."
            login_config["password"] = password
            login_config["user_id"] = details['userID']
            click.echo(msg)

    else:
        msg = f"{Fore.RED}{Style.BRIGHT}Error! {Fore.BLUE}{Style.NORMAL}Server returned error {Fore.YELLOW}{r.status_code}{Fore.BLUE}.\n{Fore.CYAN}{Style.BRIGHT}Response: {Fore.YELLOW}{Style.NORMAL}{r.text}"
        click.echo(msg)

    home = os.environ.get("HOME")

    login_config["username"] = username
    pickle.dump(login_config, open(f"{home}/.loopterm.login", "wb"))


@cli.command()
@click.option('--period', '-p')
def grades(period=None):
    global config
    global login_config

    host = config.get("host")
    s = Spinner("Connecting to School Loop...")
    s.start()
    # try:
    r = requests.get(f"https://{host}/mapi/report_card",
                     params={"studentID": login_config["user_id"]},
                     auth=requests.auth.HTTPBasicAuth(login_config["username"], login_config["password"]))
    """
    except Exception as e:
        s.stop()
        msg = f"{Fore.RED}{Style.BRIGHT}Fatal Error! {Fore.BLUE}{Style.NORMAL}Couldn't connect to server. Check your internet connection and the subdomain entered."
        click.echo(msg)
        sys.exit(1)
    """

    s.stop()
    data = r.json()
    grades = []
    if period:
        grades = [[pd["period"], pd["courseName"], pd["teacherName"],
                   pd["grade"], pd["score"]] for pd in data if pd["period"] == period]
    else:
        grades = [[pd["period"], pd["courseName"], pd["teacherName"],
                   pd["grade"], pd["score"]] for pd in data]
    click.echo(tabulate(
        [["#", "Course", "Teacher", "Mark", "Score"], *grades], headers="firstrow"))


if __name__ == '__main__':
    cli()
