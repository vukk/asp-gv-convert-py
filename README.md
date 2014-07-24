asp-gv-convert-py
=================

A python script to convert clasp output to JSON for the asp-gv javascript visualization script.

Why?
----

So that we can visualize ASP encodings of graph problems where the answer sets are sets of edges.
See [asp-gv visualization script](https://github.com/vukk/asp-gv).

Timestamps
----------

Timestamps can be produced with [tcat-monotonic](https://github.com/vukk/tcat-monotonic).
Just pipe it ``cat grounded_opt.asp | clasp | tcat-monotonic``.

Requirements
------------

- networkx

Use [virtualenv](http://virtualenv.readthedocs.org/en/latest/virtualenv.html) to install the requirements.
When inside the virtualenv, this can be done with ``pip install < requirements.txt``.

If something doesn't work, see requirements.txt for the specific versions required.

Options
-------

```
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
```

Examples
--------

### Converting simple clasp output, not optimizing, not timestamped and no gringo ###

Just the clasp output. Not optimizing, not timestamped.
This will create an undirected complete graph for visualization, set timedeltas to 4.0sec, and optimum value of each solution to 1.

```
./convert_outputs_to_json.py -e cycle -c example-data/tsp0_50ans/clasp_notopt_notts_out -d data.json -t time.json -s soln.json --not-opt --not-timestamped
```

### Converting clasp optimization output with timestamps, no gringo ###

This will create an undirected complete graph for visualization.
Timedeltas will be fetched from the timestamps in clasp output.

```
./convert_outputs_to_json.py -e edge -c example-data/econ0_opt/clasp_timestamped_out -d data.json -t time.json -s soln.json
```

### Converting clasp optimization output with timestamps and gringo text output ###

This will fetch the graph from gringo's textual output.
Timedeltas will be fetched from the timestamps in clasp output.

```
./convert_outputs_to_json.py -e cycle -c example-data/tsp1_opt/clasp_timestamped_out -o cost -g example-data/tsp1_opt/gringo_text_out -i -d data.json -t time.json -s soln.json
```

