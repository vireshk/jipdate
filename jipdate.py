#!/usr/bin/python2

from jira import JIRA
import json
import re
import os
import sys
from argparse import ArgumentParser

# Sandbox server
server = 'https://dev-projects.linaro.org'

# Production server, comment out this in case you want to use the real server
#server = 'https://projects.linaro.org'

def get_args():
    parser = ArgumentParser(description='Script to create images on a format \
                        that Mynewts bootloader expects')

    parser.add_argument('-c', required=False, action="store_true", \
            default=False, \
            help='Gather all Jira issue(s) assigned to you into the \
            status_update.txt file')

    return parser.parse_args()

################################################################################

def get_my_name():
    n = os.environ['JIRA_USERNAME'].split("@")[0].title()
    return n.replace(".", " ")

################################################################################

def update_jira(jira, i, c):
    print "Updating Jira issue: %s with comment:" % i
    print "-- 8< --------------------------------------------------------------------------"
    print "%s" % c
    print "-- >8 --------------------------------------------------------------------------\n\n"
    jira.add_comment(i, c)

################################################################################

message_header = """Hi,

This is the status update from me for the last week.

Cheers!
"""

def get_jira_issues(jira):
    jql = "assignee = currentUser() AND status not in (Resolved, Closed)"
    my_issues = jira.search_issues(jql)
    msg = message_header + get_my_name() + "\n\n"

    with open ("status_update.txt", "w") as f:
        f.write(msg)

        print "Found issue:"
        for issue in my_issues:
            print "%s : %s" % (issue, issue.fields.summary)
            f.write("[%s]\nREMOVE THIS LINE: %s\nNo updates since last week.\n\n" % (issue,
                issue.fields.summary))

    print "\nstatus_update.txt has been prepared with all of your open\n" + \
          "issues. Manually edit the file, then re-run this script without\n" + \
          "the '-c' parameter to update your issues."

################################################################################
def main(argv):
    args = get_args()
    try:
        username = os.environ['JIRA_USERNAME']
        password = os.environ['JIRA_PASSWORD']
    except KeyError:
        print "Forgot to export JIRA_USERNAME and JIRA_PASSWORD?"
        sys.exit()

    credentials=(username, password)
    jira = JIRA(server, basic_auth=credentials)

    if args.c:
        get_jira_issues(jira)
        sys.exit()

    # Regexp to match Jira issue on a single line, i.e:
    # [SWG-28]
    # [LITE-32]
    # etc ...
    regex = r"^\[[A-Z]+-\d+\]\n$"

    # Contains the status text, it could be a file or a status email
    status = ""

    with open("status_update.txt") as f:
        status = f.readlines()

    myissue = "";
    mycomment = "";

    # State to keep track of whether we are in an issue or a comment
    state = "issue"

    for line in status:
        # New issue?
        if re.search(regex, line):
            if state == "comment":
                update_jira(jira, myissue, mycomment)
                state = "issue"

            myissue = line.strip();
            myissue = myissue[1:-1]
            mycomment = ""
            state = "comment"
        else:
            mycomment += line

    if len(mycomment) > 0:
        update_jira(jira, myissue, mycomment)

    print "Successfully updated your Jira tickets!"

if __name__ == "__main__":
        main(sys.argv)
