import re
import os
import git
import subprocess
import sqlite3

from git_map import GitMap

class Repository:
    def execute_cmd(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        return process.communicate()[0].strip()
        
    def new_subprocess(self, cmd):
        cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        return cmd

    def __init__(self):
        self.repo = git.Repo(os.getcwd())

        self.bug_regex = re.compile('.*[bB][uU][gG].*')
        self.wl_regex = re.compile('.*[wW][lL].*')

        self.repo_path = self.repo.working_dir
        self.repo_name = self.repo.working_dir.split('/')[-1]
        self.db_file_path = self.repo_path + '/' + self.repo_name + '.db'

        if not os.path.isfile(self.db_file_path):
            self.git_map = GitMap()
            new_repo = True
        else:
            self.git_map = None
            new_repo = False

        self.conn = sqlite3.connect(self.db_file_path)

        self.conn.execute('''CREATE TABLE IF NOT EXISTS branch (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME CHAR(50),
            LAST_REMOTE_COMMIT CHAR(50),
            TYPE CHAR(10),
            UNIQUE(NAME)
        );''')

        self.conn.commit()
        self.load_current_branch()

    def calculate_branch_details(self, branch):
        if not self.git_map:
            self.git_map = GitMap()
        
        ref = next( (x for x in self.git_map.refs if x['ref'].name == branch), None)
        last_remote_commit = ref['fork']
        
        if self.bug_regex.match(branch):
            type = 'b'
        elif self.wl_regex.match(branch):
            type = 'w'
        else:
            type = '?'
            
        return {
            'name': branch,
            'last_remote_commit': last_remote_commit,
            'type': type
        }

    def calculate_current_branch_details(self):
        current_branch = self.repo.head.ref.name
        return self.calculate_branch_details(current_branch)

    def fetch_branch(self, branch):
        stmt = 'SELECT * FROM branch WHERE NAME = ?'
        cursor = self.conn.execute(stmt, (branch,))
        data = cursor.fetchone()

        if not data:
            return None
        else:
            return {
                'name': data[1],
                'last_remote_commit': data[2],
                'type': data[3]
            }

    def register_branch(self, branch, type, last_remote_commit):
        print "Registering branch " + branch
        stmt = 'INSERT OR IGNORE INTO branch (NAME, LAST_REMOTE_COMMIT, TYPE) VALUES(?, ?, ?)'
        self.conn.execute(stmt, (branch, last_remote_commit, type,))
        self.conn.commit()

    def unregister_branch(self, branch, type):
        print "Un-Registering branch " + branch
        stmt = 'DELETE FROM branch WHERE NAME = ? AND TYPE = ?'
        self.conn.execute(stmt, (branch, type,))
        self.conn.commit()

    def load_current_branch(self):
        self.current_branch = self.repo.head.ref.name
        data = self.fetch_branch(self.current_branch)

        if not data:
            data = self.calculate_current_branch_details()

        self.branch_type = data['type']
        self.last_remote_commit = data['last_remote_commit']

    def new_branch(self, new_branch, parent_branch = None):
        if not parent_branch:
            parent_branch = self.current_branch

        print "Creating new branch " + new_branch + " from " + parent_branch
        status = subprocess.call("git checkout -b " + data[0], shell=True)
        if status == 0:
            self.register_branch(data[0], data[1], self.last_remote_commit)
            print "Success"
        else:
            print "ERROR creating new " + "Bug" if type == "B" else "Worklog" +"!"

    def delete_branch(self, data, type):
        status = subprocess.call("git branch -d " + data[0], shell=True)
        if status == 0:
            self.unregister_branch(data[0], type)
            print "Success"
        else:
            print "ERROR deleting " + "Bug" if type == "B" else "Worklog" +"!"

    def list_branches(self, type):
        cmd = ['git', 'branch', '--list']
        if type == 'b':
            cmd.append('*[Bb][uU][gG]*')
        else:
            cmd.append('*[Ww][Ll]*')

        data = re.sub(r'[\s\*]+', ' ', self.execute_cmd(cmd))
        for branch in data.split():
            if branch == self.current_branch:
                print '* ' + branch
            else:
                print branch

    def is_remote_branch(self, branch):
        process = self.new_subprocess(["git", "rev-parse", "--verify", "origin/" + branch])
        return process.returncode == 0

    def is_on_remote_branch(self):
        return self.is_remote_branch(self.current_branch)

    # MAIN REPO FUNCTIONS:
    def checkout(self, data):
        cmd = ['git', 'checkout', data[0]]
        subprocess.call(cmd)
        self.load_current_branch()

    def diff(self, data):
        if not self.last_remote_commit:
            cmd = ['git', 'diff']
        else:
            cmd = ['git', 'diff', self.last_remote_commit + '..']
        subprocess.call(cmd)
        
    def parent(self, data):
        print self.last_remote_commit

    def patch(self, data):
        if not self.last_remote_commit:
            cmd = ['git', 'diff']
        else:
            cmd = ['git', 'diff', self.last_remote_commit + '..']
        diff = self.execute_cmd(cmd)
        
        if diff == "":
            print "No Diff Bruh"
            return;
        
        try:
            patch_dir = self.repo_path + '/patches'
            patch_file = patch_dir + '/' + self.current_branch.split('/')[-1] + '.diff'
            if not os.path.exists(patch_dir):
                os.makedirs(patch_dir)
            
            file = open(patch_file, 'w+')
            file.write(diff)
        except:
            print "Error creating patch"
            
        print "Patch created at: " + patch_file
        
    def changes(self, data):
        if not self.last_remote_commit:
            cmd = ['git', 'diff', '--name-status']
        else:
            cmd = ['git', 'diff', '--name-status', self.last_remote_commit + '..']
        changes = self.execute_cmd(cmd)
        
        for change in sorted(changes.split('/n')):
            print change
        
    # WORKLOG FUNCTIONS:
    def list_worklogs(self, data):
        self.list_branches('w')
        
    def delete_worklog(self, data):
        self.delete_branch(data, 'w')
        
    def new_worklog(self, data):
        data.append('w')

        if len(data) == 2:
            parent = data[1]
            if not self.is_remote_branch(parent):
                print parent + " is not a remote branch!"
                return
            
            process = self.new_subprocess(['git', 'checkout', parent])
            if process.returncode != 0:
                print parent + " does not exist!"
            else:
                self.new_branch(data)
        elif self.is_on_remote_branch():
            self.new_branch(data)
        else:
            print "Cannot be on local branch to create new Worklog!"
        
    # BUG FUNCTIONS:
    
    def list_bugs(self, data):
        self.list_branches('b')
        
    def delete_bug(self, data):
        self.delete_branch(data, 'b')
        
    def new_bug(self, data):
        data.append('b')

        if len(data) == 2:
            parent = data[1]
            if not self.is_remote_branch(parent):
                print parent + " is not a remote branch!"
                return
            
            process = self.new_subprocess(['git', 'checkout', parent])
            if process.returncode != 0:
                print parent + " does not exist!"
            else:
                self.new_branch(data)
        elif self.is_on_remote_branch():
            self.new_branch(data)
        else:
            print "Cannot be on local branch to create new Bug!"
    
