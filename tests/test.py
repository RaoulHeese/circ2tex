import glob
import os

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT

from circ2tex.common import StyleData
from circ2tex.representation import Converter
from circ2tex.textools import LualatexCompiler
from circ2tex.tikzengine import TikzEngine


def test_all_styles(style_data, representation, renderer, compiler):
    file_dir = 'out'
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    for style_name in style_data.style_names:
        style_dict = style_data.style_dict(style_name)
        post_action = lambda tex_file_dict: compiler.compile_collection(tex_file_dict, file_dir,
                                                                        lambda file_name: f'{file_name}_{style_name}')
        tex_file_dict = renderer.render(representation, style_dict, post_action=post_action)
        print(f'built: {", ".join([tex_file.name for tex_file in tex_file_dict.values()])}')


def generate_test_circuit(num_qubits, enable_h, decompose):
    circuit = QuantumCircuit(num_qubits)
    if enable_h:
        for i in range(num_qubits):
            circuit.h(i)
    qft = QFT(num_qubits=num_qubits)
    if decompose:
        qft = qft.decompose()
    circuit.append(qft, range(num_qubits), None)
    circuit = qft
    circuit.name = f'qft_{num_qubits}{"_h" if enable_h else ""}{"_d" if decompose else ""}'
    circuit.measure_all()
    return circuit


def run_test():
    circuits = []

    for num_qubits in [2, 10]:
        for enable_h in [False]:
            for decompose in [True, False]:
                circuits.append(generate_test_circuit(num_qubits, enable_h, decompose))

    style_data = StyleData(list(glob.glob('../examples/styles/*_style.json')))

    representation = Converter().convert(circuits)

    renderer = TikzEngine()

    compiler = LualatexCompiler()

    test_all_styles(style_data, representation, renderer, compiler)


if __name__ == '__main__':
    run_test()
