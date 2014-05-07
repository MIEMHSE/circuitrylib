# CircuitryLib

**A Python library for creating and modelling various сircuit engineering systems (digital logic circuits for now).**

Author: The Profitware Group / Sergey Sobko <S.Sobko@profitware.ru>
The code is mainly written as a part of my very special coursework at Moscow Institute of Electronics and Mathematics (MIEM HSE).

## Introduction

This library provides interface for creating and modelling various сircuit engineering systems (digital logic circuits for now). It provides output to LaTeX, graphical representations, graphs and MATLAB code that generates Simulink models. It works with Python version 2.7. Other versions are not tested yet.

## Building

From source:

Install the dependencies:

- [SymPy](http://sympy.org/)
- [Pillow](http://python-imaging.github.io/) (maintained PIL fork)
- [NumPy](http://www.numpy.org/)
- [NetworkX](http://networkx.github.io/)
- [MatplotLib](http://matplotlib.org/)

Alternatively use `pip`:

    $ pip install -r requirements.txt

## Getting the code

The code is hosted at [GitHub](https://github.com/profitware/circuitrylib).

Check out the latest development version anonymously with:

```
 $ git clone git://github.com/profitware/circuitrylib.git
 $ cd circuitrylib
```

## Using

The library provides classes for circuitry elements: basic digital logic gates and devices like multiplexers and adders. It also supports output to LaTeX. Graphical output is planned.

*Multiplexer example:*

First import necessary modules:
```
>>> from circuitry.devices.mux import DeviceMux
>>> from circuitry.adapters.latex.mux import DeviceMuxLatexTruthTableAdapter
>>> from circuitry.adapters.matlab.extended import ExtendedMatlabAdapter
>>> from circuitry.adapters.visual.symbol import ElectronicSymbolAdapter
```

To create multiplexer device with two strobe signal slots, three address signal slots, eight data signal slots and one straight output signal slot:
```
>>> device_mux = DeviceMux(strobe_signals='v:2',
                           address_signals='a:3',
                           data_signals='d:8',
                           output_signals='y:1',
                           strobe_signals_subs=dict(v0=1, v1=0),
                           output_signals_subs=dict(y0=1))
```

To create truth table for multiplexer and output it to LaTeX:
```
>>> device_mux_latex_truth_table = DeviceMuxLatexTruthTableAdapter(device_mux)
>>> print (r'\begin{tabular}{%(latex_columns)s}\\\hline\\%(latex_columns_names)s\\' +
           r'\hline\\%(latex_table)s\hline\\\end{tabular}') % \
        {'latex_columns': device_mux_latex_truth_table.latex_columns,
         'latex_columns_names': device_mux_latex_truth_table.latex_columns_names,
         'latex_table': device_mux_latex_truth_table.latex_table}
```

To show electronic symbol for multiplexer:
```
>>> ElectronicSymbolAdapter(device_mux).image.show()
```

To produce MATLAB code that generates Simulink model:
```
>>> mux_schematics = ExtendedMatlabAdapter(device_mux)
>>> print '\n'.join(mux_schematics.matlab_code())
```

To create adder device with one strobe signal slot, augend of 4 slots, addend of 4 slots and output of 6 slots (4 bits + OF + OF for two's complement):
```
>>> device_adder = DeviceAdd(strobe_signals='v:1',
                             first_signals='f:4',
                             second_signals='s:4',
                             output_signals='d:6',
                             strobe_signals_subs=dict(v0=1))
```

## TODO

Patches and bug reports are [welcome](https://github.com/profitware/circuitrylib/issues/new), just please keep the style consistent with the original source.

To be implemented in further releases:

* Library of elements.
* Analog devices.
* Timing and simulation.
* Graphical output.
* Documentation and tests.