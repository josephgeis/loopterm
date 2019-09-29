#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from spinner import Spinner
import sys
import os
import base64
import pickle

import click
import requests
import colorama
from colorama import Fore, Style
from tabulate import tabulate


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


def grade_report(period, zeros=False):
    global config
    global login_config

    host = config.get("host")
    s = Spinner("Connecting to School Loop...")
    s.start()
    # try:
    rc = requests.get(f"https://{host}/mapi/report_card",
                      params={"studentID": login_config["user_id"]},
                      auth=requests.auth.HTTPBasicAuth(login_config["username"], login_config["password"]))

    rc_data = rc.json()
    course_data = None
    try:
        course_data = [[pd["period"], pd["courseName"], pd["teacherName"],
                        pd["grade"], pd["score"], pd["periodID"]] for pd in rc_data if pd["period"] == period][0]
    except IndexError:
        s.stop()
        click.echo(f"{Fore.YELLOW}You don't have a period {period} class.")
        sys.exit()

    course_id = course_data[5]
    teacher = course_data[2]
    course_name = course_data[1]

    rr = requests.get(f"https://{host}/mapi/progress_report",
                      params={
                          "studentID": login_config["user_id"],
                          "periodID": course_id
                      },
                      auth=requests.auth.HTTPBasicAuth(login_config["username"], login_config["password"]))
    s.stop()

    pr = rr.json()[0]

    mark = pr["grade"]
    precision = pr["precision"]
    score = round(float(pr["score"])*100, int(precision))

    uncolored_grades = []
    try:
        uncolored_grades = [[assignment["assignment"]["title"], assignment["percentScore"], assignment.get("score", "-"),
                             assignment["assignment"]["maxPoints"], assignment["comment"], assignment["assignment"]["categoryName"]] for assignment in pr["grades"]]
    except KeyError:
        pass

    if zeros:
        def is_zero(g):
            try:
                return float(g[2]) == 0
            except Exception:
                return False
        uncolored_grades = [
            g for g in uncolored_grades if is_zero(g)]

    grades = []
    for grade in uncolored_grades:
        g = []
        if grade[2] == "-":
            g.insert(0, f"{Fore.YELLOW}{grade[0]}")
            g.insert(1, f"{Fore.YELLOW}{grade[1]}")
            g.insert(2, f"{Fore.YELLOW}{grade[2]}")
            g.insert(3, f"{Fore.YELLOW}{grade[3]}")
            g.insert(4, f"{Fore.YELLOW}{grade[4]}")
            g.insert(5, f"{Fore.YELLOW}{grade[5]}")

        elif float(grade[2]) == 0:
            g.insert(0, f"{Fore.RED}{grade[0]}")
            g.insert(1, f"{Fore.RED}{grade[1]}")
            g.insert(2, f"{Fore.RED}{grade[2]}")
            g.insert(3, f"{Fore.RED}{grade[3]}")
            g.insert(4, f"{Fore.RED}{grade[4]}")
            g.insert(5, f"{Fore.RED}{grade[5]}")
        else:
            g.insert(0, f"{Fore.RESET}{grade[0]}")
            g.insert(1, f"{Fore.RESET}{grade[1]}")
            g.insert(2, f"{Fore.RESET}{grade[2]}")
            g.insert(3, f"{Fore.RESET}{grade[3]}")
            g.insert(4, f"{Fore.RESET}{grade[4]}")
            g.insert(5, f"{Fore.RESET}{grade[5]}")
        grades.append(g)

    if zeros:
        click.echo(
            f"{Fore.RED}{Style.BRIGHT}Zeros Report for {Fore.BLUE}{Style.NORMAL}{course_name}")
        if len(grades) == 0:
            click.echo(
                f"{Fore.GREEN}{Style.BRIGHT}No Zeros!")
        elif len(grades) == 1:
            click.echo(
                f"{Fore.RED}{Style.BRIGHT}{len(grades)} Zero")
        else:
            click.echo(
                f"{Fore.RED}{Style.BRIGHT}{len(grades)} Zeros")
    else:
        click.echo(
            f"{Fore.GREEN}{Style.BRIGHT}Progress Report for {Fore.BLUE}{Style.NORMAL}{course_name}")
    click.echo(
        f"{Fore.MAGENTA}{Style.BRIGHT}{mark} {Fore.YELLOW}{Style.NORMAL}{score}%")
    click.echo(
        f"{Fore.GREEN}{Style.BRIGHT}Teacher: {Fore.BLUE}{Style.NORMAL}{teacher}")

    if len(grades) > 0:
        click.echo(tabulate(
            [["Assignment", "%", "Points", "Max Pts.", "Comment", "Category"], *uncolored_grades], headers="firstrow"))
    else:
        click.echo(f"{'-'*19}\n{Fore.YELLOW}No grades recorded.")


@cli.command()
@click.argument('period')
@click.option('--zeros', '-0', flag_value='zeros', default=False)
def report(period, zeros=False):
    grade_report(period, zeros)


@cli.command()
@click.argument('period')
def zeros(period):
    grade_report(period, True)


if __name__ == '__main__':
    cli()
