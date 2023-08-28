""""""""
Circ2Tex
""""""""

Circ2Tex is a very prototypical Python tool to convert quantum circuits (currently only from Qiskit) to tex code (
currently only based on TikZ) for visualization purposes. The goal is to produce highly configurable code that is easy
to read or to modify. It is only developed as a hobby project and not regularly maintained.

============
Installation
============

Clone this repository. Run ``tests/test.py`` to test the program, pdfs are generated in ``tests/out/``.

===========
Style files
===========

The appearance is controlled by style files in ``json`` format. A few example style files (demonstrating different features)
are included in ``examples/styles``.

========
Examples
========

--------------------------
1. QFT in different styles
--------------------------

The generated tex code changes depending on the chosen style.

QFT as a single gate
--------------------

QASM code for the circuit:

.. code-block::

    OPENQASM 2.0;
    include "qelib1.inc";
    gate gate_QFT q0,q1 { h q1; cp(pi/2) q1,q0; h q0; swap q0,q1; }
    qreg q[2];
    creg meas[2];
    gate_QFT q[0],q[1];
    barrier q[0],q[1];
    measure q[0] -> meas[0];
    measure q[1] -> meas[1];

Resulting representation in three styles (``plain``, ``dark``, ``sketch``):

.. image:: https://github.com/RaoulHeese/circ2tex/blob/main/docs/img/circuits-1.png?raw=true
    :alt: Circuit

QFT decomposed into elementary gates
------------------------------------

QASM code for the circuit:

.. code-block::

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

Resulting representation in three styles (``plain``, ``dark``, ``sketch``):

.. image:: https://github.com/RaoulHeese/circ2tex/blob/main/docs/img/circuits-2.png?raw=true
    :alt: Circuit

---------------------------
2. Modification of the code
---------------------------

The generated tex code can be easily modified. Annotations can be added conveniently by using TikZ labels
that a generated automatically for each gate.

For example, consider the following circuit representation:

.. image:: https://github.com/RaoulHeese/circ2tex/blob/main/docs/img/circuits-3a.png?raw=true
    :alt: Circuit

The corresponding tex code for the gate placement looks like this:

.. code-block:: tex

    % ...
	% gates
	% gate #0: h (Q:[4]|C:[]) @ 0 (0-0/4-4)
	\gateB{r0x0y4}{r0x0y4}{r0x0y4}{r0x0y4}{h}{gate0}
	% gate #1: cp (Q:[4, 3]|C:[]) @ 0 (1-1/3-4)
	\gatecB[qal=r0x1y4,qar=r0x1y4,qbl=r0x1y3,qbr=r0x1y3]{r0x1y3}{r0x1y3}{r0x1y4}{r0x1y4}{cp}{gate1}
	% gate #2: h (Q:[3]|C:[]) @ 0 (2-2/3-3)
	\gateB{r0x2y3}{r0x2y3}{r0x2y3}{r0x2y3}{h}{gate2}
	% gate #3: cp (Q:[4, 2]|C:[]) @ 0 (3-3/2-4)
	\gatecB[qal=r0x3y4,qar=r0x3y4,qbl=r0x3y2,qbr=r0x3y2]{r0x3y2}{r0x3y2}{r0x3y4}{r0x3y4}{cp}{gate3}
	% gate #4: cp (Q:[3, 2]|C:[]) @ 0 (4-4/2-3)
	\gatecB[qal=r0x4y3,qar=r0x4y3,qbl=r0x4y2,qbr=r0x4y2]{r0x4y2}{r0x4y2}{r0x4y3}{r0x4y3}{cp}{gate4}
	% gate #5: h (Q:[2]|C:[]) @ 0 (5-5/2-2)
	\gateB{r0x5y2}{r0x5y2}{r0x5y2}{r0x5y2}{h}{gate5}
    % ...

After manually adding a few additional lines of code to the tex file using the labels ``gate0``, ``gate1`` and so on, the annotated circuit representation looks like this:

.. image:: https://github.com/RaoulHeese/circ2tex/blob/main/docs/img/circuits-3b.png?raw=true
    :alt: Circuit

