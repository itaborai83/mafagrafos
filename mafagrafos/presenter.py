
class GraphPresenter:
        
    def __init__(self, graph):
        self.graph = graph
    
    def compute_pcts(self):
        for node in self.graph.nodes:
            from_label = node.label
            edges_sum = node.get_attr('ammount')
            
            for out_node_id in node.out_edges:
                to_label = self.graph.get_node_by_id(out_node_id).label
                edge = self.graph.get_edge(from_label, to_label)
                edges_sum += edge.get_attr('ammount')
            
            for out_node_id in node.out_edges:
                to_label = self.graph.get_node_by_id(out_node_id).label
                edge = self.graph.get_edge(from_label, to_label)
                edge_pct = edge.get_attr('ammount') / edges_sum * 100.0
                edge_pct_txt = '{:.3f}%'.format(edge_pct) 
                edge.set_attr('pct', edge_pct)
                edge.set_attr('pct_txt', edge_pct_txt)
                    
    def process_node(self, node):
        ammount = node.get_attr('ammount')
        label = self.in_double_quotes(node.label + "\\n$" + str(ammount))
        line = "    " + self.in_double_quotes(node.label) + "[label=" + label + "]; // node_id = " + str(node.node_id)
        return line, 
        
    def process_edge(self, edge):
        from_node = self.graph.get_node_by_id(edge.from_id)
        to_node = self.graph.get_node_by_id(edge.to_id)
        from_label = self.in_double_quotes(from_node.label)
        to_label = self.in_double_quotes(to_node.label)
        ammount = edge.get_attr('ammount')
        pct = edge.get_attr('pct_txt')
        time = edge.get_attr('time')
        time_txts = map(lambda t: f"T{t}", time)
        time_txts = ", ".join(list(time_txts))
        edge_label = self.in_double_quotes(time_txts +"\\n$" + str(ammount) + "\\n" + pct )
        line = "    " + from_label + " -> " + to_label +  "[label=" + edge_label + "]; "
        return line,
        
    def generate_dot(self):
        lines = []
        graph_name = self.in_double_quotes(self.graph.name)
        lines.append("digraph " + graph_name + "{")
        lines.append(f"    node[shape = rect];")
        lines.append(f"    rankdir=BT;")
        for node in self.graph.nodes:
            for line in self.process_node(node):
                lines.append(line)
        for edge in self.graph.iter_ordered_edges():
            for line in self.process_edge(edge):
                lines.append(line)
        lines.append("}")
        return "\n".join(lines)
        
    def in_double_quotes(self, obj):
        result = str(obj).replace('"', '').replace("'", "")
        result = '"' + result + '"'
        return result
