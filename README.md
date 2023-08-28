# Circ2Tex

Circ2Tex is a very prototypical Python tool to convert quantum circuits (currently only from Qiskit) to tex code (
currently only based on TikZ) for visualization purposes. The goal is to produce highly configurable code that is easy
to read or to modify. It is only developed as a hobby project and not regularly maintained.

## Installation

Clone this repository. Run _tests/test.py_ to test the program, pdfs are generated in _tests/out/_.

## Style files

The appearance is controlled by style files in json format. A few example style files (demonstrating different features)
are included.

## Examples

### 1. QFT in different styles

```
OPENQASM 2.0;
include "qelib1.inc";
gate gate_QFT q0,q1 { h q1; cp(pi/2) q1,q0; h q0; swap q0,q1; }
qreg q[2];
creg meas[2];
gate_QFT q[0],q[1];
barrier q[0],q[1];
measure q[0] -> meas[0];
measure q[1] -> meas[1];
```

.. image:: https://github.com/RaoulHeese/circ2tex/blob/main/docs/img/circuits-1.png?raw=true
:alt: Circuit

```
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg meas[2];
h q[1];
cp(pi/2) q[1],q[0];
h q[0];
swap q[0],q[1];
barrier q[0],q[1];
measure q[0] -> meas[0];
measure q[1] -> meas[1];
```

.. image:: https://github.com/RaoulHeese/circ2tex/blob/main/docs/img/circuits-2.png?raw=true
:alt: Circuit

### 2. Modification of the code

The resulting tex code can be easily modified. For example, annotations can be added conveniently by using TikZ labels
that a generated automatically for each gate.

Output:

.. image:: https://github.com/RaoulHeese/circ2tex/blob/main/docs/img/circuits-3a.png?raw=true
:alt: Circuit

After adding some additional lines of code to the tex file:

.. image:: https://github.com/RaoulHeese/circ2tex/blob/main/docs/img/circuits-3b.png?raw=true
:alt: Circuit