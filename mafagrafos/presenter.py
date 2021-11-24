
class GraphPresenter:
        
    def __init__(self, graph):
        self.graph = graph
    
    # this is wrong
    #def compute_pcts(self):
    #    # TODO: change this calculatiom from here
    #    for node in self.graph.nodes:
    #        from_label = node.label
    #        edges_sum = node.get_attr('ammount').current_value
    #        
    #        for out_node_id in node.out_edges:
    #            to_label = self.graph.get_node_by_id(out_node_id).label
    #            edge = self.graph.get_edge(from_label, to_label)
    #            edges_sum += edge.get_attr('ammount').current_value
    #        
    #        for out_node_id in node.out_edges:
    #            to_label = self.graph.get_node_by_id(out_node_id).label
    #            edge = self.graph.get_edge(from_label, to_label)
    #            edge_pct = edge.get_attr('ammount').current_value / edges_sum * 100.0
    #            edge_pct_txt = '{:.3f}%'.format(edge_pct) 
    #            edge.set_attr('pct', edge_pct)
    #            edge.set_attr('pct_txt', edge_pct_txt)
                    
    def process_node(self, node):
        ammounts_txt = []
        times = set()
        
        for node_id in node.out_edges:
            out_node = node.graph.get_node_by_id(node_id)
            edge = node.graph.get_edge(node.label, out_node.label)
            assert edge
            edge_times = edge.get_attr('time')
            for time in edge_times:
                times.add(time)

        for node_id in node.in_edges:
            in_node = node.graph.get_node_by_id(node_id)
            edge = node.graph.get_edge(in_node.label, node.label)
            assert edge
            edge_times = edge.get_attr('time')
            for time in edge_times:
                times.add(time)
        
        ammounts_txt = []
        for time in sorted(times):
            ammount = node.get_attr('ammount').value_at(time)
            ammount_txt = f"${ammount}@T{time}"
            ammounts_txt.append(ammount_txt)
        ammounts_txt = ",\\n".join(ammounts_txt)
        label = self.in_double_quotes(node.label + "\\n" + ammounts_txt)
        line = "    " + self.in_double_quotes(node.label) + "[label=" + label + "]; // node_id = " + str(node.node_id)
        return line, 
        
    def process_edge(self, edge):
        from_node = self.graph.get_node_by_id(edge.from_id)
        to_node = self.graph.get_node_by_id(edge.to_id)
        from_label = self.in_double_quotes(from_node.label)
        to_label = self.in_double_quotes(to_node.label)

        times = edge.get_attr('time')
        ammounts_txt = []
        for time in times:
            ammount = edge.get_attr('ammount').value_at(time)
            ammount_txt = f"${ammount}@T{time}"
            ammounts_txt.append(ammount_txt)
        ammounts_txt = ",\\n".join(ammounts_txt)
        edge_label = self.in_double_quotes(ammounts_txt)
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
