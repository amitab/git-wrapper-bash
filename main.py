import os
import sys
import sqlite3
import subprocess
from repository import Repository

# print 'Number of arguments:', len(sys.argv), 'arguments.'
# print 'Argument List:', str(sys.argv)

# main_options = ['parent', 'diff', 'patch', 'bug', 'wl', 'changes']
# bug_options = ['new', 'delete', 'checkout', 'list', 'edit-description', 'show-description']

status = subprocess.call(["git", "status"], stdout=subprocess.PIPE)
if status != 0:
    print "Not a Git repo!"
    exit()

repo = Repository()

# MANAGE MAIN REPOS DATABASE
conn = sqlite3.connect('repos.db')

conn.execute('''CREATE TABLE IF NOT EXISTS repo (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    REPO CHAR(50),
    REPO_PATH CHAR(50),
    REPO_HASH CHAR(50)
)''')

conn.close()

bug_options = {
    'new': repo.new_bug,
    'delete': repo.delete_bug,
    'list': repo.list_bugs
}

worklog_options = {
    'new': repo.new_worklog,
    'delete': repo.delete_worklog,
    'list': repo.list_worklogs
}

main_options = {
    'checkout': repo.checkout,
    'diff': repo.diff
}

if(sys.argv[1] == 'bug'):
    bug_options[sys.argv[2]](sys.argv[3:])
elif(sys.argv[1] == 'wl'):
    worklog_options[sys.argv[2]](sys.argv[3:])
else:
    main_options[sys.argv[1]](sys.argv[2:])