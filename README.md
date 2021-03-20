# Requirements
- Python 3.6 or above
    - Pygame
    - Numpy

# Background
This is the software used in this conference paper, studying the effectiveness
of various contact tracing methods on disease spread.

The simulation has four models of agent behaviour, with each mode building on
the previous one to form a more complete response:
- Mode A: No Reaction
- Mode B: Self-Isolation
- Mode C: Contact Tracing
- Mode D: Cautious Isolation with Geonotfication

Additionally, there are three levels of disease severity:
- 1: Mild
- 2: Moderate
- 3: Severe

For more details on these modes and severities, please see the paper.


# Running
To begin a simulation, run the command `python3 window.py {Mode} {Severity}`.
For example, to run a simulation where the agents perform contact tracing and
the disease has moderate severity, run `python3 window.py C 2`.
Parameters such as world size, number of agents, and simulation duration in
ticks can be modified in `simulation_parameters.py`.

# Logs and Plotting
After finishing, the engine will dump logs locally to a subdirectory of `logs`, 
named in the pattern `modeX_sevY`, where X and Y are the response mode and 
severity identifiers, respectively. Please note that the simulation will throw
an error before starting if logs from a previous run with the same values 
already exist; this is a precaution to avoid overwriting results.

To generate plots from the dumped data, run `python3 plotter.py {directory}`, 
where `{directory}` is the name of the log folder as described above. 

