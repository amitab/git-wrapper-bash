import re
import subprocess

class BranchTree:
    def new_subprocess(self, cmd):
        cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        return cmd
        
    def __init__(self):
        
        self.branch_tree = self.new_subprocess(['git', 'log', '--graph', 
            '--abbrev-commit', '--decorate' , 
            "--format=format:'%H- %an%d'", 
            '--all', '--first-parent']).communicate()[0].strip()
            
        self.branch_tree = self.branch_tree.split('\n')
        
        for b in self.branch_tree:
            print b
            
    def find_commit_level(self, line):
    
    def is_converging(self, line):    
    
    def decipher_tree(self):
        refs = []
        
        for b in self.branch_tree:
        
b = BranchTree()