# vim: set ts=4 sw=4 tw=0 et :

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import networkx as nx
from networkx.readwrite import json_graph as nxjson

from distutils.dir_util import mkpath

import re
import os, os.path, sys

### REGEXP STRINGS

RE_TIME     = '(\d+\.\d+)'
RE_OPTNUM   = 'Optimization: (\d+)'
RE_ANSWER   = 'Answer: (\d+)'
RE_SOLVING  = 'Solving...'
RE_PRED_2   = '\((\w+),(\w+)\)'         # Accept all names, not only \d+
RE_PRED_3   = '\((\w+),(\w+),(\w+)\)'


### THE PRIMARY FUNCTION

def files_to_json(
        chosen_pred,
        clasp_filename,
        clasp_is_timestamped,
        clasp_is_optimizing,
        cost_pred,
        gringo_text_filename,
        is_directed,
        json_data_filename,
        json_time_filename,
        json_soln_filename
    ):

    edge_id_map = None
    costs       = None

    # If "gringo -t" output is given, then we use that.
    if gringo_text_filename and cost_pred:
        costs = parse_costs_from_gringo_text(
            cost_pred, gringo_text_filename
        )
    # Otherwise, if we do not have the graph information, default to
    # using an undirected fully connected graph (ie. complete graph).
    # We parse the node names from the clasp answer file.
    else:
        nodes = parse_nodes_from_solution_file(
            chosen_pred, clasp_filename, clasp_is_timestamped
        )
        nodes, edges, costs = create_complete_graph(nodes)
        is_directed = False

    # Just a check that nothing went wrong...
    if costs == None or len(costs) == 0:
        return (False, 'Costs can not be None or length 0')

    # Create a dictionary that, when converted to JSON, is compatible with
    # the vis.js javascript library.
    visjs_json_dict, edge_id_map = create_visjs_dict(
        costs, is_directed
    )

    # Create two assisiting dictionaries:
    # - timing the animation: the time differences between answers
    # - edge sets: which edges belong to which answer
    # These dictionaries are also converted to JSON later.
    timing_dict, answer_sets_dict = create_timing_and_answer_set_dicts(
        chosen_pred, clasp_filename,
        clasp_is_timestamped, clasp_is_optimizing, edge_id_map
    )

    # Create directories for the JSON files, if they do not exist.
    mkpath(os.path.dirname(json_data_filename))
    mkpath(os.path.dirname(json_time_filename))
    mkpath(os.path.dirname(json_soln_filename))

    # Save the JSON files.
    # Write the graph to a JSON file.
    with open(json_data_filename, 'w') as fh:
        nxjson.dump(visjs_json_dict, fh, indent=2)
    # Write the timings to a JSON file.
    with open(json_time_filename, 'w') as fh:
        nxjson.dump(timing_dict, fh, indent=2)
    # Write the solutions to a JSON file.
    with open(json_soln_filename, 'w') as fh:
        nxjson.dump(answer_sets_dict, fh, indent=2)

    return (True, 'Success')



### HELPER FUNCTIONS

def create_predicate_re(pred_name, size):
    # Define regexp for answer sets.
    if size == 2:
        regexp = pred_name + RE_PRED_2
    elif size == 3:
        regexp = pred_name + RE_PRED_3
    else:
        raise Exception('The programmer was lazy :-(')
    regexp_line = '(' + regexp + ')+'
    return (regexp, regexp_line)

# For convenience, a re.match iteration hackety hack.
def rematch(pattern, input):
    matches = re.match(pattern, input)
    if matches:
        yield matches

def separate_timestamp(line):
    match = re.match('^' + RE_TIME + '\s+(.*)$', line)
    if match:
        return match.group(1,2)
    else:
        return None

def create_complete_graph_num_nodes(num_nodes):
    return create_connected_graph( range(1, num_nodes + 1) )

def create_complete_graph(nodes):
    all = [ [(n1, n2) for n2 in nodes if n1 != n2] for n1 in nodes ]
    edges = [item for sublist in all for item in sublist] # flatten
    costs = [ ( e[0], e[1], 1) for e in edges ]
    return (nodes, edges, costs)

def parse_nodes_from_solution_file(chosen_pred, filename, is_timestamped):
    chosen_pred_re, chosen_pred_line_re = create_predicate_re(chosen_pred, 2)

    fh = open(filename, 'r')
    nodes = {}

    # Find all nodes from the set of chosen edges.
    for orig_line in fh:
        if is_timestamped:
            time, line = separate_timestamp(orig_line)
        else:
            time = "0.0" # dummy val
            line = orig_line

        for m in rematch(chosen_pred_line_re, line):
            edges = line.strip().split(' ')
            for edge in edges:
                match = re.match(chosen_pred_re, edge)
                nodes[match.group(1)] = 1
                nodes[match.group(2)] = 1

    fh.close()
    return nodes.keys()

def parse_costs_from_gringo_text(cost_pred, filename):
    cost_pred_re, _ = create_predicate_re(cost_pred, 3)
    
    fh = open(filename, 'r')
    costs = set()

    # Find edges and their costs.
    for line in fh:
        match = re.match(cost_pred_re, line)
        if match:
            costs.add( match.group(1,2,3) )

    fh.close()
    return costs

def create_visjs_dict(costs, is_directed):
    # networkx graph instance.
    G = None
    if is_directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()

    # Add edges.
    G.add_weighted_edges_from( list(costs) )

    # Create a neato layout positions.
    positions = nx.graphviz_layout(G, prog="neato")

    # Create a vis.js compatible dictionary.
    # Add nodes first.
    d = dict(
        nodes = [
            {
                "id": str(n), # vis.js does not need str()
                "label": "n"+str(n),
                "x": positions[n][0]*10,
                "y": positions[n][1]*10,
                "allowedToMoveX": True,
                "allowedToMoveY": True,
            }
            for n in G.nodes() ],
        edges = []
    )

    # If the graph is directed, find out which edges are two way, and which
    # are one way.
    if is_directed:
        twoway = set( [ e for e in G.edges() if e[1] in G.pred[e[0]] ] )
        oneway = twoway.symmetric_difference( set(G.edges()) )
        twoway = set( [ e for e in twoway if e[0] <= e[1] ] ) # filter
    # Otherwise everything is two way (undirected).
    else:
        twoway = set( G.edges() )
        oneway = set()

    # Append edges to the vis.js compatible dictionary.
    # TODO: scale edge weights to [0.N, N]
    d['edges'].extend(
        [
            {
                "id": str(id),
                "from": str(u),
                "to": str(v),
                "width": G.edge[u][v]['weight'],
                "label": G.edge[u][v]['weight'],
            }
        for id, (u,v) in enumerate(twoway, 1) ]
    )
    d['edges'].extend(
        [
            {
                "id": str(id),
                "from": str(u),
                "to": str(v),
                "style": 'arrow',
                "width": G.edge[u][v]['weight'],
                "label": G.edge[u][v]['weight'],
            }
        for id, (u,v) in enumerate(oneway, 1+len(d['edges'])) ]
    )

    edge_id_map = dict()
    for id, e in enumerate(twoway, 1):
        edge_id_map[e] = id
    for id, e in enumerate(oneway, 1+len(edge_id_map)):
        edge_id_map[e] = id

    return (d, edge_id_map)


def create_timing_and_answer_set_dicts(
        chosen_pred, clasp_file, is_timestamped, is_optimizing, edge_id_map
        ):
    chosen_pred_re, chosen_pred_line_re = create_predicate_re(chosen_pred, 2)

    # Open the solution file.
    fh = open(clasp_file, 'r')

    # Init values.
    times       = {}    # dict of: id -> (time, optimization, answer)
    chosen      = {}    # dict of: id -> [edge(X,Y), ...]
    start_time  = 0.0
    answer      = None
    answer_time = None
    result      = []
    optimum     = None

    # Find solutions, ugly "parsing".
    for orig_line in fh:
        if is_timestamped:
            time, line = separate_timestamp(orig_line)
        else:
            time = "0.0" # dummy val
            line = orig_line

        # Abuse iterators.
        # Function rematch yields either one match obj, or nothing.

        # Start counting time when clasp starts the solving process.
        for m in rematch(RE_SOLVING, line):
            start_time = float(time)
        # Catch the answer set number.
        for m in rematch(RE_ANSWER, line):
            answer = m.group(1)
            if is_timestamped:
                answer_time = float(time) - start_time
            else:
                answer_time = 4.0
        # Catch the set of edge IDs in this answer set.
        for m in rematch(chosen_pred_line_re, line):
            edges = line.strip().split(' ')
            for edge in edges:
                mo = re.match(chosen_pred_re, edge)
                tup = mo.group(1,2)
                if edge_id_map.has_key(tup):
                    edgeid = edge_id_map[tup]
                else:
                    edgeid = edge_id_map[mo.group(2,1)]
                result.append( edgeid )
            
            if not is_optimizing: # ugly hack
                # if not optimizing then
                # save
                times[answer] = (answer_time, "1")
                chosen[answer] = result
                # reinit
                answer      = None
                answer_time = None
                result      = []
                optimum     = None
        # Catch the optimization value.
        # IF we are optimizing, then:
        # This is the last line of one set, so it triggers a save.
        for m in rematch(RE_OPTNUM, line):
            optim = m.group(1)
            # save
            times[answer] = (answer_time, optim)
            chosen[answer] = result
            # reinit
            answer      = None
            answer_time = None
            result      = []
            optimum     = None

    # endfor

    fh.close()
    return (times, chosen)


# EOF

