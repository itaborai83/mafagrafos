from mafagrafos.node import Node
from mafagrafos.edge import Edge
from mafagrafos.paths import Segment, Path

class StopSearch(Exception):pass

class NodeVisitor:
        
    def __init__(self, graph):
        self.graph = graph
        self.visited_set = set()

    def visit(self, node_id):
        assert node_id not in self.visited_set
        self.visited_set.add(node_id)
        
    def unvisit(self, node_id):
        assert node_id in self.visited_set
        self.visited_set.remove(node_id)
    
    def has_visited(self, node_id):
        return node_id in self.visited_set
        
    def clear_visited(self):
        self.visited_set.clear()

    def dfs(self, node_id, upper_bound):
        self.has_loop = False
        try:
            self._dfs(node_id, upper_bound)
            return False # loop was not created
        except StopSearch: 
            return True # loop was created
            
    def _dfs(self, node_id, upper_bound):
        # DFS - Make a DFS traversal to mark all nodes reachable from node_id and mark
        #  all nodes affected by the edge insertion. These nodes will later get new
        #  topological indexes by means of the shift method.
        self.visit(node_id)
        node = self.graph.get_node_by_id(node_id)
        for succ_node_id in node.out_edges:
            topo_idx = self.graph.get_topo_index(node_id)
            if topo_idx == upper_bound: # should this be >= ???
                # when a successor node has the same topo index as the upper bound of the
                # affected area, it means that a cycle has been detected, so we should stop
                # processing the adding of the edge to the graph                
                raise StopSearch()
            
            if self.has_visited(succ_node_id):
                # skip visited nodes
                continue
            
            if topo_idx < upper_bound:
                self._dfs(succ_node_id, upper_bound)
    
    def shift(self, lower_bound, upper_bound):
        # Shift - Renumber the nodes so that the topological ordering is preserved
        # sanity check inputs
        assert lower_bound < upper_bound
        assert 0 <= lower_bound < self.graph.next_node_id - 1, (lower_bound, self.graph.next_node_id)
        assert 0 <  upper_bound < self.graph.next_node_id
        tail_nodes = []
        # for each intermediary element in the unadjusted topological ordering
        current = lower_bound
        shift_ammount = 0
        while current <= upper_bound:
            # get index of node at topological index current.
            current_node_id = self.graph.index_to_node[ current ]
            current_node = self.graph.get_node_by_id(current_node_id)
            assert current_node is not None

            if self.has_visited(current_node_id):
                # the node has been visited in the last dfs run,
                # which means there is path from from_node -> current node (this is statement is probably wrong)
                # either before or after the introduction of the edge from_node -> to_node.
                self.unvisit(current_node_id) # why is it necessary to unvisit it???
                # save to push it to the tail of the affected region later
                tail_nodes.append(current_node_id)
                # keep track of how much space is shifted
                shift_ammount += 1
            else:
                # the current node was not touched during the last dfs run,
                # which means that there is no path from from_node -> current_node (this is statement is probably wrong)
                # either before or after the introduction of the edge from_node -> to_node.

                # change the topological index of the unvisited node to make room
                topo_idx = current - shift_ammount # off by 1 errors?
                self.allocate(current_node_id, topo_idx)
                  
            current = current + 1
        
        # process the tail end of the affected region
        for j in range(len(tail_nodes)):
            self.allocate(tail_nodes[j], current - shift_ammount)
            current += 1
            
    def allocate(self, node_id, topo_idx):
        # assign the topological index to the node n.
        self.graph.node_to_index[ node_id ] = topo_idx
        self.graph.index_to_node[ topo_idx ] = node_id
            
class Graph:
    
    __slots__ = ["name", "allow_cycles", "next_node_id", "nodes", "labels", "node_to_index", "index_to_node", "edges", "edge_order", "visitor", "data"]
    
    SHOW_PATH_BUILDING = False
    
    def __init__(self, name, allow_cycles=False):
        assert name
        self.name               = name
        self.allow_cycles       = allow_cycles # can't be changed
        self.next_node_id       = 0
        self.nodes              = []
        self.labels             = {}
        self.node_to_index      = None if allow_cycles else []
        self.index_to_node      = None if allow_cycles else []
        self.edges              = {}
        self.edge_order         = []
        self.visitor            = None if allow_cycles else NodeVisitor(self)
        self.data               = {}
        
    def __str__(self):
        return f"<Graph name='{self.name}>'"
    
    def __repr__(self):
        return f"<Graph name='{self.name}>'"

    def get_data(self):
        return self.data

    def get_attr(self, attr):
        return self.data.get(attr, None)
        
    def set_attr(self, attr, value):
        self.data[attr] = value
        
    def _create_node(self, node_id, label, data=None):
        node = Node(node_id, label, data=data)
        node.graph = self
        return node

    def _create_edge(self, from_node, to_node, edge_label=None, data=None):
        edge = Edge(from_node.node_id, to_node.node_id, label=edge_label, data=data)
        edge.graph = self
        return edge
        
    def get_node_by_label(self, label):
        # can return None
        return self.labels.get(label, None)

    def get_node_by_id(self, node_id):
        # can not return None. if you have the node_id it *must* exist
        assert 0 <= node_id < self.next_node_id
        return self.nodes[node_id]
    
    def get_topo_index(self, node_id):
        assert not self.allow_cycles
        assert 0 <= node_id < self.next_node_id
        return self.node_to_index[node_id]
        
    #def start_topo_sorting(self):
    #    assert self.topo_sort_started == False
    #    node_count = len(self.nodes)
    #    assert node_count > 0
    #    self.topo_sort_started = True
    #    if self.allow_cycles:
    #        return
    #    for idx in range(node_count):
    #        self.node_to_index[idx] = idx
    #        self.index_to_node[(node_count - 1) - idx] = idx # why does the index to node need to descend???
        
    def add_node(self, label, data=None):
        assert label
        assert self.get_node_by_label(label) is None
        node = self._create_node(self.next_node_id, label, data)
        self.nodes.append(node)
        self.labels[node.label] = node
        self.next_node_id += 1
        assert len(self.nodes) == self.next_node_id
        if self.allow_cycles:
            return node
        else:
            # update the trivial topological sorting of a graph without edges
            # node to index mapping - indicates the topological index of node n
            self.node_to_index.append(node.node_id)
            # index to node mapping - indicates the node which occupies the nth topological index
            self.index_to_node.append(node.node_id)
            assert len(self.node_to_index)  == self.next_node_id
            assert len(self.index_to_node)  == self.next_node_id
            return node
    
    def get_edge(self, from_label, to_label):
        assert from_label
        assert to_label
        from_node = self.get_node_by_label(from_label)
        assert from_node is not None
        to_node = self.get_node_by_label(to_label)
        assert to_node is not None
        edge_key = (from_node.node_id, to_node.node_id)
        return self.edges.get(edge_key, None)
    
    def has_edge(self, from_label, to_label):
        assert from_label
        assert to_label
        from_node = self.get_node_by_label(from_label)
        assert from_node is not None
        to_node = self.get_node_by_label(to_label)
        assert to_node is not None
        return (from_node.node_id, to_node.node_id) in self.edges
    
    def iter_ordered_edges(self):
        for edge_key in self.edge_order:
            yield self.edges[ edge_key ]
            
    def add_edge(self, from_label, to_label, edge_label=None, data=None, allow_cycles=False):
        assert from_label
        assert to_label
        from_node = self.get_node_by_label(from_label)
        assert from_node is not None
        to_node = self.get_node_by_label(to_label)
        assert to_node is not None
        if from_node == to_node and not self.allow_cycles:
            return None

        edge = self._create_edge(from_node, to_node, edge_label=edge_label, data=data)
        from_node.add_out_edge(to_node.node_id)
        to_node.add_in_edge(from_node.node_id)
        edge_key = (from_node.node_id, to_node.node_id)
        self.edges[ edge_key ] = edge
        self.edge_order.append(edge_key)
        if self.allow_cycles:
            return edge
            
        # find the affected region of the topological ordering according with the MNR algorithm
        lower_bound = self.get_topo_index(to_node.node_id)
        upper_bound = self.get_topo_index(from_node.node_id)
        if lower_bound >= upper_bound:
            # the recently added edge did not alter the current topological sorting
            # we are done for now
            return edge # edge added, no cycle was created
        # if the topological sorting needs updating
        self.visitor.clear_visited()
        loop_created = self.visitor.dfs(to_node.node_id, upper_bound)
        if loop_created:
            # delete edge
            from_node.del_out_edge(to_node.node_id)
            to_node.del_in_edge(from_node.node_id)
            del self.edges[ edge_key ]
            self.edge_order.pop(-1)
            return None
        self.visitor.shift(lower_bound, upper_bound)
        #print(from_label, '->', to_label)
        #print(self.node_to_index)
        #print(self.index_to_node)
        return edge
        
    def build_paths(self, sink_label):
        # graph is a DAG, so no cycles
        assert not self.allow_cycles
        head_node = self.get_node_by_label(sink_label)
        assert head_node
        curr_path = Path()
        acc = []
        self._build_path(head_node, None, None, curr_path, acc)
        return acc
        
    def _build_path(self, head_node, edge, tail_node, curr_path, acc):
        if self.SHOW_PATH_BUILDING:
            print(head_node)
            print(edge)
            print(tail_node)
            for segment in curr_path.segments:
                print("\t", segment)
            print()
        
        if curr_path.segment_count > 0 and not curr_path.is_temporally_consistent():
            # if the head node is the head of a temporally inconsistent path.
            # recompute the edge percentual taking into account the received_ammount of the tail_node
            # and then pop off the head node from the path
            
            curr_path = None # throw away the current path and adjust the last added path
            curr_path = acc[-1]
            head_node = tail_node # previous head node
            tail_node_label = curr_path.segments[0].to_label
            tail_node = self.get_node_by_label(tail_node_label) # previous tail node
            edge = self.get_edge(head_node.label, tail_node.label) # previous edge linking previous head node to tail node
            assert edge
            
            # compute the edge pct of a temporally inconsistent node
            edge_ammount        = edge.get_attr('ammount')
            node_ammount        = head_node.get_attr('ammount')
            received_ammount    = head_node.get_attr('received_ammount') # get inputed_ammount from all descending nodes
            inputed_ammount     = head_node.get_attr('inputed_ammount')
            transferred_ammount = head_node.get_attr('transferred_ammount')
            #edge_pct            = edge_ammount / (node_ammount + received_ammount)
            edges_sum           = transferred_ammount + inputed_ammount
            # discount the received_ammount because it is has not happened yet
            edges_sum          -= received_ammount 
            edge_pct            = edge_ammount / edges_sum
            
            # the pct stored within the graph needs to be updated            
            # TODO: put this in a saner place
            edge_pct_txt = '{:.2f}%'.format(edge_pct*100.0) 
            edge.set_attr('pct', edge_pct)
            edge.set_attr('pct_txt', edge_pct_txt)
            
            curr_path.inputed_ammount   = inputed_ammount
            curr_path.received_ammount  = received_ammount
            curr_path.segments[0].pct   = edge_pct
            # since the head not is not temporally consistent, stop building this path
            # do not read the path to the accumulator
            return
        
        elif curr_path.segment_count > 0 and curr_path.is_temporally_consistent():
            # if the head node is the head of a temporally consistent path.
            # use the precomputed edge percentual. DO NOT take into account the received_ammount of the tail_node
            curr_path.received_ammount  = 0.0
            curr_path.inputed_ammount   = head_node.get_attr('inputed_ammount')
            acc.append(curr_path)

        # continue processing a temporally consistent path with 1 or more nodes in the path
        old_path = curr_path
        new_tail_node = head_node
        for from_id in new_tail_node.in_edges:
            # retrieve the start node of the edge
            new_head_node = self.get_node_by_id(from_id)
            assert new_head_node
            # use the node label to retrieve the edge itself
            edge = self.get_edge(new_head_node.label, new_tail_node.label)
            assert edge
            # retrieve the edge_pct
            edge_pct = edge.get_attr('pct') / 100.0
            assert edge_pct
            # retrieve the fista and last transfer time from the edge
            min_t = edge.get_attr('time')[0]
            max_t = edge.get_attr('time')[-1]
            assert min_t <= max_t
            # create a new path cloning the old path 
            curr_path = old_path.clone()
            # push a new segment onto the first position of the current path
            segment = Segment(new_head_node.label, new_tail_node.label, edge_pct, min_t, max_t)
            curr_path.push_segment(segment)
            self._build_path(new_head_node, edge, new_tail_node, curr_path, acc)
        