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
            "--format=format:'[%H] %d'", 
            '--all', '--first-parent']).communicate()[0].strip()
            
        self.branch_tree = self.branch_tree.split('\n')
        data = self.build_db()
        self.refs = data[0]
        self.commit_map = data[1]
            
    def find_line_level(self, line):    
        level = 1
        for char in line:
            if char == '*':
                break
            if char == '|':
                level = level + 1
        return level
        
    def converge_to_level(self, line):
        level = 0
        for char in line:
            if char == '/' or char == '*':
                break
            if char == '|':
                level = level + 1
        return level
    
    def build_db(self):
        refs = {}
        convergence = []
        orphans = []

        branches = {}
        commit_map = {}

        for index, b in enumerate(self.branch_tree):
            commit_index = b.find('*')
            converge_index = b.find('/')
            hash_match = re.search('\[(.*)\]', b)
            ref_match = re.search('\((.*)\)', b)
            level = self.find_line_level(b)

            if not level in branches:
                branches[level] = []
            if ref_match:
                branches[level].append({
                    'ref_name': ref_match.groups()[0],
                    'commits': []
                })

            if commit_index >= 0:
                for branch in branches[level]:
                    branch['commits'].append(hash_match.groups()[0])
                    
                i = 0
                while i < (len(orphans)):
                    orphan = orphans[i]
                    if orphan['converge_to'] == level:
                        #print "Found Orphan " + orphan['ref'] + " to converge to " + str(level) + " : " + hash_match.groups()[0]
                        refs[orphan['ref']]['converge_to'] = level
                        refs[orphan['ref']]['found_converge'] = True
                        refs[orphan['ref']]['parent_commit_hash'] = hash_match.groups()[0]
                        orphans.remove(orphan)
                    else:
                        i += 1
                
                i = 0        
                while i < (len(convergence)):
                    converge = convergence[i]
                    if converge['converge_to'] != None:
                        if level == converge['converge_to']:
                            #print "Found waiting convergence " + converge['ref'] + " to converge to " + str(level) + " : " + hash_match.groups()[0]
                            refs[converge['ref']]['converge_to'] = level
                            refs[converge['ref']]['found_converge'] = True
                            refs[converge['ref']]['parent_commit_hash'] = hash_match.groups()[0]
                        else:
                            #print "Found waiting convergence " + converge['ref'] + " orphaned"
                            orphans.append(converge)
                        
                        convergence.remove(converge)
                    else:
                        i += 1
            
            if ref_match:
                ref_name = ref_match.groups()[0]
                #print "New ref: " + ref_name
                convergence.append({
                    'ref': ref_name,
                    'converge_to': None
                })
                
                refs[ref_name] = {
                    'name': ref_name,
                    'converged': False,
                    'parent_commit_hash': None,
                    'parent_branch_ref': None,
                    'found_converge': False, # once we find parent commit
                    'level': level,
                    'converge_to': None # once we find the level it converged to
                }
                
            elif converge_index > 0 and len(convergence) > 0:
                if  self.branch_tree[index - 1].find('/') == -1:
                    for branch in branches[self.converge_to_level(b) + 1]:
                        commit_map[branch['ref_name']] = branch['commits']
                    del branches[self.converge_to_level(b) + 1][:]
                common_refs_level = refs[convergence[-1]['ref']]['level']
                for converge in convergence:
                    if b.find('|') == -1:
                        refs[converge['ref']]['level'] = refs[converge['ref']]['level'] - 1
                    elif refs[converge['ref']]['level'] == common_refs_level:
                        converge['converge_to'] = self.converge_to_level(b)
                        #print "Found convergence: " + converge['ref'] + " to " + str(self.converge_to_level(b))
        
        # Finally add the last ref's commits
        commit_map[branches[1][0]['ref_name']] = branches[1][0]['commits']
        
        for ref_name in refs:
            print refs[ref_name]['name'] + ' -> ' + str(refs[ref_name]['parent_commit_hash'])
        
        return (refs, commit_map)
            
b = BranchTree()
# print b.commit_map
# print b.refs