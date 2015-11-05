import os
import sys
import sqlite3
import subprocess
import hashlib

class Repository:
    def execute_cmd(self, cmd):
        cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        return cmd.communicate()[0].strip()

    def __init__(self):
        self.current_branch = self.execute_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        self.repo_path = self.execute_cmd(['git', 'rev-parse', '--show-toplevel'])
        self.repo_name = self.repo_path.split('/')[-1]
        self.conn = sqlite3.connect(self.repo_name + '.db')
        
        self.conn.execute('''CREATE TABLE IF NOT EXISTS branch (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            WORK_BRANCH CHAR(50),
            DESC CHAR(50),
            TYPE CHAR(1),
            LAST_REMOTE_COMMIT CHAR(50)
        )''')
        
        sha1 = hashlib.sha1()
        sha1.update(self.repo_path + ' ' + str(os.stat(self.repo_path).st_ctime))
        self.repo_hash = sha1.hexdigest()
        
        self.last_remote_commit = self.execute_cmd(['git', 'reflog', 'show', '--pretty=format:%H', self.current_branch]).split('\n')[-1]
        self.load_branches()
        
    def load_branches(self):
        cursor = self.conn.execute("SELECT * FROM branch")
        self.branches = {}
        for row in cursor:
            self.branches[row[1]] = {
                'curr_branch': row[1],
                'desc': row[2],
                'type': row[3],
                'last_remote_commit': row[4]
            }
            
    def new_branch(self, data, type):
        stmt = 'INSERT INTO branch(WORK_BRANCH, DESC, TYPE, LAST_REMOTE_COMMIT) VALUES(?, ?, ?, ?)'
        status = subprocess.call("git checkout -b " + data[0], shell=True)
        if status == 0:
            self.conn.execute(stmt, (data[0], data[1] if len(data) == 2 else "", type, self.last_remote_commit))
            self.conn.commit()
        else:
            print "ERROR creating new " + "Bug" if type == "B" else "Worklog" +"!"
        
    def delete_branch(self, data, type):
        stmt = 'DELETE FROM branch WHERE WORK_BRANCH = ? AND TYPE = ?'
        status = subprocess.call("git branch -d " + data[0], shell=True)
        if status == 0:
            self.conn.execute(stmt, (data[0], type,))
            self.conn.commit()
        else:
            print "ERROR deleting " + "Bug" if type == "B" else "Worklog" +"!"
        
    def list_branches(self, type):
        cmd = ['git', 'branch', '--list']
        if type == 'B':
            cmd.append('*[Bb][uU][gG]*')
        else:
            cmd.append('*[Ww][Ll]*')
        
        print self.execute_cmd(cmd)
    # MAIN REPO FUNCTIONS:
    
    def checkout(self, data):
        cmd = ['git', 'checkout', data[0]]
        subprocess.call(cmd)

    def diff(self, data):
        cmd = ['git', 'diff', self.last_remote_commit + '..']
        subprocess.call(cmd)
        # branch = self.branches[self.current_branch]
        # print branch
        # if self.current_branch in self.branches.keys():
        #     branch = self.branches[self.current_branch]
        #     print branch
        #     cmd = ['git', 'diff', branch['last_remote_commit'] + '..']
        #     subprocess.call(cmd)
        # else:
        #     print "Branch not a Bug or a Worklog!"
        
    # WORKLOG FUNCTIONS:
    
    def list_worklogs(self, data):
        self.list_branches('W')
        
    def delete_worklog(self, data):
        self.delete_branch(data, 'W')
        
    def new_worklog(self, data):
        self.new_branch(data, 'W')
        
    # BUG FUNCTIONS:
    
    def list_bugs(self, data):
        self.list_branches('B')
        
    def delete_bug(self, data):
        self.delete_branch(data, 'B')
        
    def new_bug(self, data):
        self.new_branch(data, 'B')
    
