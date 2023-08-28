import re

from circ2tex.common import StyledObject, ItemDict


class RepresentationObject(StyledObject):
    def __init__(self, name):
        super().__init__()
        if name is None:
            name = ''
        self._name = name

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return f'{self.__name__}(name={self._name})'


class CollectionRepresentation(RepresentationObject):
    style_key_default = '*'
    style_key_collection = 'items'
    style_char_regex = '~'

    def __init__(self, name):
        super().__init__(name)

    @classmethod
    def _reset_item_dict_style(cls, item_dict):
        for item in item_dict.values():
            item.reset_style()

    @classmethod
    def _update_item_dict_style(cls, item_dict, style_dict):
        for item_idx, item in item_dict.items():
            item_name = item.name.lower()
            named_style_dict = None
            if item_name in style_dict:
                named_style_dict = style_dict[item_name]
            elif item_idx in style_dict:
                named_style_dict = style_dict[item_idx]
            else:
                for key, value in style_dict.items():
                    if key[0] == cls.style_char_regex and re.search(key[1:], item_name) is not None:
                        named_style_dict = value
                        break
            if named_style_dict is None:
                if cls.style_key_default in style_dict:
                    named_style_dict = style_dict[cls.style_key_default]
                else:
                    named_style_dict = dict()
            item.update_style(**named_style_dict)


class BitRegister(RepresentationObject):
    def __init__(self, name):
        super().__init__(name)
        self._bit_index_dict = ItemDict()

    @property
    def bit_index_dict(self):
        return self._bit_index_dict

    @property
    def n_bits(self):
        return max(self._bit_index_dict.keys())

    def add_bit(self, bit_index, index=None):
        assert bit_index not in self._bit_index_dict.values()
        return self._bit_index_dict.add_item(bit_index, index)


class QubitRegister(BitRegister):
    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return f'QuantumRegister(name={self._name}, bit_indices={"[" + ", ".join([f"{index_in_register}:{bit_index}" for index_in_register, bit_index in self._bit_index_dict.items()]) + "]"})'


class ClbitRegister(BitRegister):
    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return f'ClassicalRegister(name={self._name}, bit_indices={"[" + ", ".join([f"{index_in_register}:{bit_index}" for index_in_register, bit_index in self._bit_index_dict.items()]) + "]"})'


class RegisterCollection(CollectionRepresentation):
    style_key_qgregs = 'qgregs'
    style_key_cgregs = 'cgregs'

    def __init__(self, name):
        super().__init__(name)
        self._qreg_dict = ItemDict()
        self._creg_dict = ItemDict()

    @property
    def qreg_dict(self):
        return self._qreg_dict

    @property
    def creg_dict(self):
        return self._creg_dict

    def __repr__(self):
        return f'RegisterCollection(name={self.name}, QuantumRegisters={"{" + ", ".join([f"{idx}: {repr(qreg)}" for idx, qreg in self._qreg_dict.items()]) + "}"}, ClassicalRegisters={"{" + ", ".join([f"{idx}: {repr(creg)}" for idx, creg in self._creg_dict.items()]) + "}"})'

    def reset_style(self):
        self._reset_item_dict_style(self._qreg_dict)
        self._reset_item_dict_style(self._creg_dict)
        self._reset_style()

    def update_style(self, **kwargs):
        style_dict = dict(**kwargs)

        # qregs
        self._update_item_dict_style(self._qreg_dict,
                                     style_dict.get(self.style_key_qgregs, dict()).get(self.style_key_collection,
                                                                                       dict()))
        style_dict.pop(self.style_key_qgregs, None)

        # cregs
        self._update_item_dict_style(self._creg_dict,
                                     style_dict.get(self.style_key_cgregs, dict()).get(self.style_key_collection,
                                                                                       dict()))
        style_dict.pop(self.style_key_cgregs, None)

        # general
        self._update_style(**style_dict)

    def add_qreg(self, qreg, index=None):
        return self._qreg_dict.add_item(qreg, index)

    def add_creg(self, creg, index=None):
        return self._creg_dict.add_item(creg, index)


class Bit(RepresentationObject):
    def __init__(self, name):
        super().__init__(name)
        self._register_index_dict = ItemDict()

    @property
    def register_indices(self):
        return self._register_index_dict

    def add_to_register(self, register_index, index_in_register):
        return self._register_index_dict.add_item(index_in_register, register_index)


class Qubit(Bit):
    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return f'QuantumBit(name={self._name}, registers={"[" + ", ".join([f"{qreg_index}:{index_in_qreg}" for qreg_index, index_in_qreg in self._register_index_dict.items()]) + "]"})'


class Clbit(Bit):
    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return f'ClassicalBit(name={self._name}, registers={"[" + ", ".join([f"{creg_index}:{index_in_creg}" for creg_index, index_in_creg in self._register_index_dict.items()]) + "]"})'


class BitCollection(CollectionRepresentation):
    style_key_qubits = 'qubits'
    style_key_clbits = 'clbits'

    def __init__(self, name):
        super().__init__(name)
        self._qubit_dict = ItemDict()
        self._clbit_dict = ItemDict()

    @property
    def qubit_dict(self):
        return self._qubit_dict

    @property
    def clbit_dict(self):
        return self._clbit_dict

    def __repr__(self):
        return f'BitCollection(name={self.name}, QuantumBits={"{" + ", ".join([f"{idx}: {repr(qubit)}" for idx, qubit in self._qubit_dict.items()]) + "}"}, ClassicalBits={"{" + ", ".join([f"{idx}: {repr(clbit)}" for idx, clbit in self._clbit_dict.items()]) + "}"})'

    def reset_style(self):
        self._reset_item_dict_style(self._qubit_dict)
        self._reset_item_dict_style(self._clbit_dict)
        self._reset_style()

    def update_style(self, **kwargs):
        style_dict = dict(**kwargs)

        # qubits
        self._update_item_dict_style(self._qubit_dict,
                                     style_dict.get(self.style_key_qubits, dict()).get(self.style_key_collection,
                                                                                       dict()))
        style_dict.pop(self.style_key_qubits, None)

        # clbits
        self._update_item_dict_style(self._clbit_dict,
                                     style_dict.get(self.style_key_clbits, dict()).get(self.style_key_collection,
                                                                                       dict()))
        style_dict.pop(self.style_key_clbits, None)

        # general
        self._update_style(**style_dict)

    def add_qubit(self, q, index=None):
        return self._qubit_dict.add_item(q, index)

    def add_clbit(self, c, index=None):
        return self._clbit_dict.add_item(c, index)


class Gate(RepresentationObject):
    def __init__(self, name, qubit_indices, clbit_indices, params, label):
        super().__init__(name)
        self._qubit_indices = qubit_indices
        self._clbit_indices = clbit_indices
        self._params = params
        self._label = label

    @property
    def qubit_indices(self):
        return self._qubit_indices

    @property
    def clbit_indices(self):
        return self._clbit_indices

    @property
    def params(self):
        return self._params

    @property
    def label(self):
        if self._label is not None:
            return self._label
        else:
            return self.name

    @property
    def is_measurement_gate(self):
        return self.name.lower() == 'measure'

    def __repr__(self):
        return f'Gate(name={self._name}, qubits={"[" + ", ".join([str(qubit_index) for qubit_index in self._qubit_indices]) + "]"}, clbits={"[" + ", ".join([str(clbit_index) for clbit_index in self._clbit_indices]) + "]"})'

    def _get_default_style_dict(self):
        return dict(width=1)

    def reset_style(self):
        self._reset_style()

    def update_style(self, **kwargs):
        style_dict = dict(**kwargs)

        # general
        self._update_style(**style_dict)


class GateCollection(CollectionRepresentation):
    def __init__(self, name):
        super().__init__(name)
        self._gate_dict = ItemDict()

    @property
    def gate_dict(self):
        return self._gate_dict

    def __repr__(self):
        return f'GateCollection(name={self.name}, gates={"{" + ", ".join([f"{idx}: {repr(gate)}" for idx, gate in self._gate_dict.items()]) + "}"})'

    def reset_style(self):
        self._reset_item_dict_style(self._gate_dict)
        self._reset_style()

    def update_style(self, **kwargs):
        style_dict = dict(**kwargs)

        # gates
        self._update_item_dict_style(self._gate_dict, style_dict.get(self.style_key_collection, dict()))
        style_dict.pop(self.style_key_collection, None)

        # general
        self._update_style(**style_dict)

    def add_gate(self, gate, index=None):
        return self._gate_dict.add_item(gate, index)


class Circuit(RepresentationObject):
    style_key_regs = 'regs'
    style_key_bits = 'bits'
    style_key_gates = 'gates'

    def __init__(self, name):
        super().__init__(name)
        self._regs = RegisterCollection(None)
        self._bits = BitCollection(None)
        self._gates = GateCollection(None)

    @property
    def regs(self):
        return self._regs

    @property
    def bits(self):
        return self._bits

    @property
    def gates(self):
        return self._gates

    def __repr__(self):
        return f'Circuit(name={self._name}, RegisterCollection={repr(self._regs)}, BitCollection={repr(self._bits)}, GateCollection={repr(self._gates)})'

    def _get_default_style_dict(self):
        return dict(width=0, row_distance=1)

    def reset_style(self):
        self._regs.reset_style()
        self._bits.reset_style()
        self._gates.reset_style()
        self._reset_style()

    def update_style(self, **kwargs):
        style_dict = dict(**kwargs)

        # regs
        regs_style_dict = style_dict.get(self.style_key_regs, dict())
        self._regs.update_style(**regs_style_dict)
        style_dict.pop(self.style_key_regs, None)

        # bits
        bits_style_dict = style_dict.get(self.style_key_bits, dict())
        self._bits.update_style(**bits_style_dict)
        style_dict.pop(self.style_key_bits, None)

        # gates
        gates_style_dict = style_dict.get(self.style_key_gates, dict())
        self._gates.update_style(**gates_style_dict)
        style_dict.pop(self.style_key_gates, None)

        # general
        self._update_style(**style_dict)

    def add_qreg(self, qreg, index=None):
        return self._regs.add_qreg(qreg, index)

    def add_creg(self, creg, index=None):
        return self._regs.add_qreg(creg, index)

    def add_qubit(self, q, index=None):
        return self._bits.add_qubit(q, index)

    def add_clbit(self, c, index=None):
        return self._bits.add_clbit(c, index)

    def connect_qubit_to_qreg(self, qubit_index, qreg_index, index_in_qreg):
        self._bits.qubit_dict[qubit_index].add_to_register(qreg_index, index_in_qreg)
        self._regs.qreg_dict[qreg_index].add_bit(qubit_index, index_in_qreg)

    def connect_clbit_to_creg(self, clbit_index, creg_index, index_in_creg):
        self._bits.clbit_dict[clbit_index].add_to_register(creg_index, index_in_creg)
        self._regs.creg_dict[creg_index].add_bit(clbit_index, index_in_creg)

    def add_gate(self, gate, index=None):
        return self._gates.add_gate(gate, index)


class CircuitCollection(CollectionRepresentation):

    def __init__(self, name):
        super().__init__(name)
        self._circuit_dict = ItemDict()

    @property
    def circuit_dict(self):
        return self._circuit_dict

    def __repr__(self):
        return f'CircuitCollection(name={self.name}, circuits={"{" + ", ".join([f"{idx}: {repr(circuit)}" for idx, circuit in self._circuit_dict.items()]) + "}"})'

    def reset_style(self):
        self._reset_item_dict_style(self._circuit_dict)
        self._reset_style()

    def update_style(self, **kwargs):
        style_dict = dict(**kwargs)

        # circuits
        self._update_item_dict_style(self._circuit_dict, style_dict.get(self.style_key_collection, dict()))
        style_dict.pop(self.style_key_collection, None)

        # general
        self._update_style(**style_dict)

    def add_circuit(self, circuit, index=None):
        return self._circuit_dict.add_item(circuit, index)


class Representation(RepresentationObject):
    style_key_circuits = 'circuits'

    def __init__(self, name):
        super().__init__(name)
        self._circuits = CircuitCollection(None)

    @property
    def circuits(self):
        return self._circuits

    def __repr__(self):
        return f'Representation(name={self.name}, CircuitCollection={repr(self._circuits)})'

    def reset_style(self):
        self._circuits.reset_style()
        self._reset_style()

    def update_style(self, **kwargs):
        style_dict = dict(**kwargs)

        # circuit collection
        circuits_style_dict = style_dict.get(self.style_key_circuits, dict())
        self._circuits.update_style(**circuits_style_dict)
        style_dict.pop(self.style_key_circuits, None)

        # general
        self._update_style(**style_dict)


class Converter:
    def __init__(self):
        pass

    def _convert_qreg(self, qiskit_qreg):
        qreg = QubitRegister(qiskit_qreg.name)
        return qreg

    def _convert_creg(self, qiskit_creg):
        creg = ClbitRegister(qiskit_creg.name)
        return creg

    def _convert_qubit(self, qiskit_qubit, qiskit_circuit, qreg_map):
        qiskit_index, qiskit_qregs = qiskit_circuit.find_bit(qiskit_qubit)
        q = Qubit(None)
        qreg_indices = {}
        for qreg, index_in_qreg in qiskit_qregs:
            qreg_index = qreg_map[qreg]
            qreg_indices[qreg_index] = index_in_qreg
        return q, qiskit_index, qreg_indices

    def _convert_clbit(self, qiskit_clbit, qiskit_circuit, creg_map):
        qiskit_index, qiskit_cregs = qiskit_circuit.find_bit(qiskit_clbit)
        c = Clbit(None)
        creg_indices = {}
        for creg, index_in_qreg in qiskit_cregs:
            creg_index = creg_map[creg]
            creg_indices[creg_index] = index_in_qreg
        return c, qiskit_index, creg_indices

    def _convert_gate(self, qiskit_instruction, qiskit_qubits, qiskit_clbits, qubit_map, clbit_map):
        name = qiskit_instruction.name
        qubit_indices = [qubit_map[qiskit_qubit] for qiskit_qubit in qiskit_qubits]
        clbit_indices = [clbit_map[qiskit_clbit] for qiskit_clbit in qiskit_clbits]
        params = qiskit_instruction.params
        label = qiskit_instruction.label
        gate = Gate(name, qubit_indices, clbit_indices, params, label)
        return gate

    def _convert_circuit(self, qiskit_circuit):
        circuit = Circuit(qiskit_circuit.name)

        # quantum registers
        qreg_map = {}
        for qiskit_qreg in qiskit_circuit.qregs:
            qreg = self._convert_qreg(qiskit_qreg)
            qreg_map[qiskit_qreg] = circuit.regs.add_qreg(qreg)

        # qubits
        qubit_map = {}
        for qiskit_qubit in qiskit_circuit.qubits:
            q, qiskit_index, qreg_indices = self._convert_qubit(qiskit_qubit, qiskit_circuit, qreg_map)
            qubit_map[qiskit_qubit] = circuit.bits.add_qubit(q, qiskit_index)
            for qreg_index, index_in_qreg in qreg_indices.items():
                circuit.connect_qubit_to_qreg(qiskit_index, qreg_index, index_in_qreg)

        # classical registers
        creg_map = {}
        for qiskit_creg in qiskit_circuit.cregs:
            creg = self._convert_creg(qiskit_creg)
            creg_map[qiskit_creg] = circuit.regs.add_creg(creg)

        # clbits
        clbit_map = {}
        for qiskit_clbit in qiskit_circuit.clbits:
            c, qiskit_index, creg_indices = self._convert_clbit(qiskit_clbit, qiskit_circuit, creg_map)
            clbit_map[qiskit_clbit] = circuit.bits.add_clbit(c, qiskit_index)
            for creg_index, index_in_creg in creg_indices.items():
                circuit.connect_clbit_to_creg(qiskit_index, creg_index, index_in_creg)

        # gates
        for qiskit_instruction, qiskit_qubits, qiskit_clbits in qiskit_circuit:
            gate = self._convert_gate(qiskit_instruction, qiskit_qubits, qiskit_clbits, qubit_map, clbit_map)
            circuit.gates.add_gate(gate)

        return circuit

    def convert(self, qiskit_circuits):
        representation = Representation(None)
        for qiskit_circuit in qiskit_circuits:
            circuit = self._convert_circuit(qiskit_circuit)
            representation.circuits.add_circuit(circuit)
        return representation
