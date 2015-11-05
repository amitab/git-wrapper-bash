import re
import os
import subprocess
import sqlite3

class Repository:
    def execute_cmd(self, cmd):
        cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        return cmd.communicate()[0].strip()
        
    def new_subprocess(self, cmd):
        cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        return cmd
            
    def load_curr_branch_details(self):
        self.branch_data = self.fetch_branch(self.current_branch)
        if not self.branch_data:
            self.calc_current_branch()
            if not self.is_on_remote_branch():
                self.register_branch(self.current_branch, self.type)
        else:
            self.last_remote_commit = self.branch_data[2]
            self.type = self.branch_data[3]
            
    def __init__(self):
        db_path = os.path.dirname(os.path.realpath(__file__))
        self.bug_regex = re.compile('.*[bB][uU][gG].*')
        self.wl_regex = re.compile('.*[wW][lL].*')
        
        self.current_branch = self.execute_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        self.repo_path = self.execute_cmd(['git', 'rev-parse', '--show-toplevel'])
        self.repo_name = self.repo_path.split('/')[-1]
        
        self.conn = sqlite3.connect(db_path + '/' + self.repo_name + '.db')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS branch (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME CHAR(50),
            LAST_REMOTE_COMMIT CHAR(50),
            TYPE CHAR(10)
        );''')
        
        self.conn.commit()
        self.load_curr_branch_details()
    
    # ALL BRANCH FUNCTIONALITY
    def fetch_branch(self, branch):
        stmt = 'SELECT * FROM branch WHERE NAME = ?'
        cursor = self.conn.execute(stmt, (branch,))
        return cursor.fetchone()
        
    def calc_current_branch(self):
        self.current_branch = self.execute_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        self.last_remote_commit = self.execute_cmd(['git', 'reflog', 'show', '--pretty=format:%H', self.current_branch]).split('\n')[-1]
        #branches = self.execute_cmd(['git', 'branch', '--contains', self.last_remote_commit]).split('/n')
        
        if self.bug_regex.match(self.current_branch):
            self.type = 'b'
        elif self.wl_regex.match(self.current_branch):
            self.type = 'w'
        else:
            self.type = '?'
        
    def register_branch(self, branch, type):
        print "Registering branch " + branch
        stmt = 'INSERT INTO branch (NAME, LAST_REMOTE_COMMIT, TYPE) VALUES(?, ?, ?)'
        self.conn.execute(stmt, (branch, self.last_remote_commit, type,))
        self.conn.commit()
        
    def unregister_branch(self, branch, type):
        print "Un-Registering branch " + branch
        stmt = 'DELETE FROM branch WHERE NAME = ? AND TYPE = ?'
        self.conn.execute(stmt, (branch, type,))
        self.conn.commit()
            
    def new_branch(self, data, type):
        print "Creating new branch " + data[0] + " from " + self.current_branch
        status = subprocess.call("git checkout -b " + data[0], shell=True)
        if status == 0:
            self.register_branch(data[0], type)
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
        if type == 'B':
            cmd.append('*[Bb][uU][gG]*')
        else:
            cmd.append('*[Ww][Ll]*')
        
        data = re.sub(r'[\s\*]+', ' ', self.execute_cmd(cmd))
        for branch in data.split():
            if self.current_branch == branch:
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
        self.load_curr_branch_details()

    def diff(self, data):
        cmd = ['git', 'diff', self.last_remote_commit + '..']
        subprocess.call(cmd)
        
    def parent(self, data):
        print self.last_remote_commit

    def patch(self, data):
        cmd = ['git', 'diff', self.last_remote_commit + '..']
        diff = self.execute_cmd(cmd)
        
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
        if len(data) == 2:
            parent = data[1]
            if not self.is_remote_branch(parent):
                print parent + " is not a remote branch!"
                return
            
            process = self.new_subprocess(['git', 'checkout', parent])
            if process.returncode != 0:
                print parent + " does not exist!"
            else:
                self.new_branch(data, 'w')
        elif self.is_on_remote_branch():
            self.new_branch(data, 'w')
        else:
            print "Cannot be on local branch to create new Worklog!"
        
    # BUG FUNCTIONS:
    
    def list_bugs(self, data):
        self.list_branches('b')
        
    def delete_bug(self, data):
        self.delete_branch(data, 'b')
        
    def new_bug(self, data):
        if len(data) == 2:
            parent = data[1]
            if not self.is_remote_branch(parent):
                print parent + " is not a remote branch!"
                return
            
            process = self.new_subprocess(['git', 'checkout', parent])
            if process.returncode != 0:
                print parent + " does not exist!"
            else:
                self.new_branch(data, 'b')
        elif self.is_on_remote_branch():
            self.new_branch(data, 'b')
        else:
            print "Cannot be on local branch to create new Bug!"
    
