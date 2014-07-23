#!/usr/bin/env python
"""Convert clasp & gringo outputs to ASP-GV visualization script JSON files.

This script can be used to convert clasp (monotonically) timestamped output, and optionally gringo text output, to JSON files which are accepted by the ASP-GV javascript package.

Usage:
  ./convert_outputs_to_json.py --edge-pred=<predicate> --clasp-out=<filename>
        [(--cost-pred=<predicate> --gringo-out=<filename>) --directed]
        --json-data=<filename> --json-time=<filename> --json-soln=<filename>
        [--not-opt --not-timestamped]

Options:
  -e <predicate> --edge-pred=<predicate>      Name of the chosen edge/2
                                              predicate.
  -c <filename> --clasp-out=<filename>        Name of the file where the
                                              timestamped clasp output has
                                              been saved.
  -o <predicate> --cost-pred=<predicate>      Name of the cost/3 predicate.
  -g <filename> --gringo-out=<filename>       Name of the file where the
                                              output of "gringo -t" has
                                              been saved.
  -i --directed                               Indicates that the graph is a
                                              directed graph. If not given,
                                              the graph is assumed to be
                                              undirected.
  -d <filename> --json-data=<filename>        Path where to save the JSON
                                              file containing the graph data.
  -t <filename> --json-time=<filename>        Path where to save the JSON
                                              file containing the timing
                                              information.
  -s <filename> --json-soln=<filename>        Path where to save the JSON
                                              file containing the solutions
                                              of each optimization step.
  --not-opt                                   Flag to indicate that clasp
                                              output is not from an
                                              optimization, but still in
                                              some "smart order" that can
                                              be visualized.
  --not-timestamped                           Flag to indicate that clasp
                                              output is not prepended with
                                              a timestamp. Time delta will
                                              be 4.0 seconds.
Examples:
*  ./convert_outputs_to_json.py -e cycle -c results/tsp-1.out \\
*                               -o cost  -g ground-text/tsp-1.out -i \\
*                               -d json/tsp-1/data.json \\
*                               -t json/tsp-1/time.json \\
*                               -s json/tsp-1/soln.json
*
*  ./convert_outputs_to_json.py -e edge -c results/econ0/out \\
*                               -d json/econ0/data.json \\
*                               -t json/econ0/time.json \\
*                               -s json/econ0/soln.json
*
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from docopt import docopt

from aspgvconvert import convert

# Parse arguments.
args = docopt(__doc__, version='0.1')

# Run conversion
if convert.files_to_json(
        args['--edge-pred'],
        args['--clasp-out'],
        not args['--not-timestamped'],
        not args['--not-opt'],
        args['--cost-pred'],
        args['--gringo-out'],
        args['--directed'],
        args['--json-data'],
        args['--json-time'],
        args['--json-soln']
        ):
    print('Success!')
else:
    print('Conversion failed :(')

# EOF

