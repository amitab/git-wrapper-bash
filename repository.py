import re
import subprocess

class Repository:
    def execute_cmd(self, cmd):
        cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        return cmd.communicate()[0].strip()
        
    def new_subprocess(self, cmd):
        cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        return cmd

    def __init__(self):
        self.current_branch = self.execute_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        self.repo_path = self.execute_cmd(['git', 'rev-parse', '--show-toplevel'])
        self.repo_name = self.repo_path.split('/')[-1]
        self.last_remote_commit = self.execute_cmd(['git', 'reflog', 'show', '--pretty=format:%H', self.current_branch]).split('\n')[-1]
            
    def new_branch(self, data, type):
        status = subprocess.call("git checkout -b " + data[0], shell=True)
        if status == 0:
            print "Success"
        else:
            print "ERROR creating new " + "Bug" if type == "B" else "Worklog" +"!"
        
    def delete_branch(self, data, type):
        status = subprocess.call("git branch -d " + data[0], shell=True)
        if status == 0:
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

    def diff(self, data):
        cmd = ['git', 'diff', self.last_remote_commit + '..']
        subprocess.call(cmd)
        
    # WORKLOG FUNCTIONS:
    
    def list_worklogs(self, data):
        self.list_branches('W')
        
    def delete_worklog(self, data):
        self.delete_branch(data, 'W')
        
    def new_worklog(self, data):
        if self.is_on_remote_branch():
            self.new_branch(data, 'W')
        else:
            print "Cannot be on local branch to create new Worklog!"
        
    # BUG FUNCTIONS:
    
    def list_bugs(self, data):
        self.list_branches('B')
        
    def delete_bug(self, data):
        self.delete_branch(data, 'B')
        
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
                self.new_branch(data, 'B')
        elif self.is_on_remote_branch():
            self.new_branch(data, 'B')
        else:
            print "Cannot be on local branch to create new Bug!"
    
