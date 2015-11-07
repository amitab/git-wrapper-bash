class GitDAG:
    def __init__(self):
        self.vertices = {}
        self.edges = {}
        
    def add_verex(self, vertex, hash):
        if not hash in self.vertices:
            self.vertices[hash] = {
                'data': vertex,
                'fork': None
            }
            self.edges[hash] = {
                'in': set(),
                'out': set()
            }
    
    def add_edge(self, hash1, hash2):
        self.edges[hash1]['out'].add(hash2)
        self.edges[hash2]['in'].add(hash1)
        
    def find_fork_of_vertex(self, vertex):
        if vertex['ref'].name.find('master') >= 0:
            return None
        
        ancestor = vertex['ref'].commit.hexsha
        while True:
            # print "Examining parent: " + ancestor
            edge = self.edges[ancestor]
            if len(edge['out']) > 1:
                return ancestor
            elif len(edge['in']) == 0:
                return None
            else:
                ancestor = iter(edge['in']).next()
                
        return fork
        
    def display(self):
        print self.vertices.keys()
        print self.edges