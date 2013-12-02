# CircuitryLib

**A Python library for creating and modelling various сircuit engineering systems.**

Author: The Profitware Group <S.Sobko@profitware.ru>

## Introduction

This library provides interface for creating and modelling various сircuit engineering systems. It provides output to LaTeX and graphical representations. It works with Python versions from 2.7. Other versions are not tested yet.

## Building

From source:

Install the dependencies:

- [SymPy](http://sympy.org/)
- [Pillow](http://python-imaging.github.io/) (maintained PIL fork)

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

The library provides classes for circuitry elements: basic digital logic gates and devices like multiplexers. It also supports output to LaTeX. Graphical output is planned.

*Multiplexer example:*

First import necessary modules:
```
>>> from circuitry.devices.mux import DeviceMux
>>> from circuitry.graphical import DefaultElectronicSymbol
>>> from circuitry.latex.mux import DeviceMuxTruthTable
```

To create multiplexer device with two strobe signal slots, three address signal slots, eight data signal slots, one straight output signal slot and one inverted output signal slot:
```
>>> device_mux = DeviceMux(strobe_signals='v:2',
                           address_signals='a:3',
                           data_signals='d:8',
                           output_signals='y:2',
                           strobe_signals_subs=dict(v0=1, v1=0),
                           output_signals_subs=dict(y0=1, y1=0))
```

To create truth table for multiplexer and output it to LaTeX:
```
>>> device_mux_latex_truth_table = DeviceMuxTruthTable(device_mux)
>>> print (r'\begin{tabular}{%(latex_columns)s}\\\hline\\%(latex_columns_names)s\\' +
           r'\hline\\%(latex_table)s\hline\\\end{tabular}') % \
        {'latex_columns': device_mux_latex_truth_table.latex_columns,
         'latex_columns_names': device_mux_latex_truth_table.latex_columns_names,
         'latex_table': device_mux_latex_truth_table.latex_table}
```

To show electronic symbol for multiplexer:
```
>>> DefaultElectronicSymbol(device=device_mux).image.show()
```

## TODO

Patches and bug reports are [welcome](https://github.com/profitware/circuitrylib/issues/new), just please keep the style consistent with the original source.

To be implemented in further releases:

* Library of elements.
* Analog devices.
* Timing and simulation.
* Graphical output.
* Documentation and tests.