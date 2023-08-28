from abc import abstractmethod

from circ2tex.engine import Engine
from circ2tex.textools import TexCode, TexFile


class TikzCircuitGridLayoutXY:

    def __init__(self):
        pass


class TikzCircuitGridLayoutBitXY(TikzCircuitGridLayoutXY):
    def __init__(self, max_row, max_x_from, max_x_to, y):
        super().__init__()
        self._max_row = max_row
        self._max_x_from = max_x_from
        self._max_x_to = max_x_to
        self._y = y

    @property
    def max_row(self):
        return self._max_row

    @property
    def max_x_from(self):
        return self._max_x_from

    @property
    def max_x_to(self):
        return self._max_x_to

    @property
    def y(self):
        return self._y


class TikzCircuitGridLayoutGateXY(TikzCircuitGridLayoutXY):
    def __init__(self, row, x_from, x_to, y_dict_qu, y_dict_cl):
        super().__init__()
        self._row = row
        self._x_from = x_from
        self._x_to = x_to
        self._y_dict_qu = y_dict_qu  # qubit_index: y pos
        self._y_dict_cl = y_dict_cl  # clbit_index: y pos

    @property
    def row(self):
        return self._row

    @property
    def x_from(self):
        return self._x_from

    @property
    def x_to(self):
        return self._x_to

    @property
    def y_dict_qu(self):
        return self._y_dict_qu

    @property
    def y_dict_cl(self):
        return self._y_dict_cl

    @property
    def y_from(self):
        return self.calc_y_from(self.y_dict_qu.values(), self.y_dict_cl.values())

    @property
    def y_to(self):
        return self.calc_y_to(self.y_dict_qu.values(), self.y_dict_cl.values())

    @classmethod
    def calc_y_list(cls, y_list_qu, y_list_cl):
        return list(y_list_qu) + list(y_list_cl)

    @classmethod
    def calc_y_from(cls, y_list_qu, y_list_cl):
        return min(cls.calc_y_list(y_list_qu, y_list_cl))

    @classmethod
    def calc_y_to(cls, y_list_qu, y_list_cl):
        return max(cls.calc_y_list(y_list_qu, y_list_cl))


class TikzCircuitGridLayout:

    def __init__(self):
        self._qubits_xy = dict()
        self._clbits_xy = dict()
        self._gate_xy = dict()
        self._row_height = 0
        self._row_width = 0
        self._num_rows = 0
        self._row_distance = 0
        self._x_scale = 1.
        self._y_scale = 1.
        self._origin_name = 'o'

    @property
    def qubits_xy(self):
        return self._qubits_xy  # index: TikzCircuitGridLayoutBitXY

    @property
    def clbits_xy(self):
        return self._clbits_xy  # index: TikzCircuitGridLayoutBitXY

    @property
    def gate_xy(self):
        return self._gate_xy  # index: TikzCircuitGridLayoutGateXY

    @property
    def row_height(self):
        return self._row_height

    @property
    def row_width(self):
        return self._row_width

    @property
    def num_rows(self):
        return self._num_rows

    @property
    def row_distance(self):
        return self._row_distance

    @property
    def origin_name(self):
        return self._origin_name

    def compile(self, circuit):
        # bit positions: q0 ... qN c (y top to bottom)
        y = 0
        qubits_y = dict()
        for qreg in circuit.regs.qreg_dict.values():
            for qubit_index in qreg.bit_index_dict.values():
                qubits_y[qubit_index] = y
                y += 1
        clbits_y = dict()
        for creg in circuit.regs.creg_dict.values():
            for clbit_index in creg.bit_index_dict.values():
                clbits_y[clbit_index] = y
                if not circuit.style.merge_clbits:
                    y += 1

        # gate grid position (y top to bottom, x left to right)
        self._gate_xy.clear()
        row_y_x = dict()
        y_x = dict()
        y_x.update({qubits_y[qubit_index]: 0 for qreg in circuit.regs.qreg_dict.values() for qubit_index in
                    qreg.bit_index_dict.values()})
        y_x.update({clbits_y[clbit_index]: 0 for creg in circuit.regs.creg_dict.values() for clbit_index in
                    creg.bit_index_dict.values()})
        self._row_width = int(circuit.style.width)
        self._row_height = max(y_x.keys()) + 1
        for gate_index, gate in circuit.gates.gate_dict.items():
            y_dict_qu = {qubit_index: qubits_y[qubit_index] for qubit_index in gate.qubit_indices}
            y_dict_cl = {clbit_index: clbits_y[clbit_index] for clbit_index in gate.clbit_indices}
            y_from = TikzCircuitGridLayoutGateXY.calc_y_from(y_dict_qu.values(), y_dict_cl.values())
            y_to = TikzCircuitGridLayoutGateXY.calc_y_to(y_dict_qu.values(), y_dict_cl.values())
            row = 0
            while True:  # method can fail if gates are too broad for the row width
                if row not in row_y_x:
                    row_y_x[row] = y_x.copy()
                y_x_gate = {y: x for y, x in row_y_x[row].items() if y >= y_from and y <= y_to}
                x_from = max(y_x_gate.values())
                x_to = (x_from + gate.style.width - 1)
                if self._row_width == 0 or x_to <= self._row_width - 1:
                    for y in y_x_gate.keys():
                        row_y_x[row][y] = x_to + 1
                    break
                for y in y_x_gate.keys():
                    row_y_x[row][y] = self._row_width
                row += 1
            self._gate_xy[gate_index] = TikzCircuitGridLayoutGateXY(row, x_from, x_to, y_dict_qu, y_dict_cl)
        if self._row_width == 0:
            self._row_width = max(row_y_x[0].values())
        self._num_rows = max([gate_xy.row for gate_xy in self._gate_xy.values()]) + 1
        self._row_distance = circuit.style.row_distance

        # bit lines
        self._qubits_xy.clear()
        self._clbits_xy.clear()
        for qreg in circuit.regs.qreg_dict.values():
            for qubit_index in qreg.bit_index_dict.values():
                bit_row = self._num_rows - 1
                bit_x_from = 0
                bit_x_to = self._row_width - 1
                bit_y = qubits_y[qubit_index]
                for gate_index, gate in circuit.gates.gate_dict.items():
                    row = self._gate_xy[gate_index].row
                    x_to = self._gate_xy[gate_index].x_to
                    if qubit_index in gate.qubit_indices and gate.is_measurement_gate:
                        bit_row = row
                        bit_x_to = x_to
                        break
                self._qubits_xy[qubit_index] = TikzCircuitGridLayoutBitXY(bit_row, bit_x_from, bit_x_to, bit_y)
        for creg in circuit.regs.creg_dict.values():
            for clbit_index in creg.bit_index_dict.values():
                bit_row = self._num_rows - 1
                bit_x_from = 0
                bit_x_to = self._row_width - 1
                bit_y = clbits_y[clbit_index]
                for gate_index, gate in circuit.gates.gate_dict.items():
                    row = self._gate_xy[gate_index].row
                    x_to = self._gate_xy[gate_index].x_to
                    if clbit_index in gate.clbit_indices and gate.is_measurement_gate:
                        bit_row = row
                        bit_x_to = x_to
                        break
                self._clbits_xy[clbit_index] = TikzCircuitGridLayoutBitXY(bit_row, bit_x_from, bit_x_to, bit_y)

        # general
        self._x_scale = circuit.style.x_scale
        self._y_scale = circuit.style.y_scale

    def coordinate_position(self, row, x, y):
        x_position = x
        y_position = - (row * (self._row_height + self._row_distance) + y)
        return x_position, y_position

    def coordinate_label(self, row, x, y):
        return f'r{row}x{x}y{y}'

    def get_grid_code(self):
        code = TexCode()
        code += f'\\coordinate ({self.origin_name}) at (0,0);'
        for row in range(self._num_rows):
            for y in range(self._row_height):
                for x in range(self._row_width):
                    (x_position, y_position) = self.coordinate_position(row, x, y)
                    x_coordinate = x_position * self._x_scale
                    y_coordinate = y_position * self._y_scale
                    coordinate_label = self.coordinate_label(row, x, y)
                    code += f'\\coordinate ({coordinate_label}) at ($({self.origin_name})+({x_coordinate},{y_coordinate})$);'
        return code


class TikzObject:

    def __init__(self):
        pass

    def is_valid(self):
        return True

    @abstractmethod
    def get_definition_code(self, **kwargs):
        raise NotImplementedError


class TikzPreamble(TikzObject):

    def __init__(self, lines):
        super().__init__()
        self._lines = lines

    @property
    def lines(self):
        return self._lines

    def get_definition_code(self):
        code = TexCode()
        for line in self.lines:
            code += f'{line}'
        return code


class NamedTikzObject(TikzObject):

    def __init__(self, name):
        super().__init__()
        self._name = name

    @property
    def name(self):
        return f'{self._name}'


class TikzColor(NamedTikzObject):

    def __init__(self, name, colormodel, colorcode):
        super().__init__(name)
        self._colormodel = colormodel
        self._colorcode = colorcode

    @property
    def color_name(self):
        return f'{self.name}'

    @property
    def colormodel(self):
        return self._colormodel

    @property
    def colorcode(self):
        return self._colorcode

    def get_definition_code(self):
        code = TexCode()
        if len(self.colormodel) > 0:
            code += f'\\definecolor{{{self.color_name}}}{{{self.colormodel}}}{{{self.colorcode}}}'
        else:
            code += f'\\colorlet{{{self.color_name}}}{{{self.colorcode}}}'
        return code


class TikzStyle(NamedTikzObject):

    def __init__(self, name, option_dict, flags):
        super().__init__(name)
        self._option_dict = option_dict
        self._flags = flags

    @property
    def style_name(self):
        return f'{self.name}'

    @property
    def option_dict(self):
        return self._option_dict

    @property
    def flags(self):
        return self._flags

    def get_definition_code(self):
        code = TexCode()
        code += f'\\tikzstyle{{{self.style_name}}}=[' + ','.join(
            [f'{key}={value}' for key, value in self.option_dict.items()] + [f'{flag}' for flag in self.flags]) + ']'
        return code


class TikzCommand(NamedTikzObject):

    def __init__(self, name, num_args, option_dict, content):
        super().__init__(name)
        self._num_args = num_args
        self._option_dict = option_dict
        self._content = content

    @property
    def num_args(self):
        return self._num_args

    @property
    def option_dict(self):
        return self._option_dict

    @property
    def group_name(self):
        return f'{self.name}'

    @property
    def macro_name(self):
        return f'\\{self.name}'

    @property
    def is_keyval_macro(self):
        return len(self.option_dict) > 0

    @classmethod
    def at_env_code_start(cls):
        return TexCode('\\makeatletter')

    @classmethod
    def at_env_code_end(cls):
        return TexCode('\\makeatother')

    def keyval_macro_name(self, key):
        return f'\\{self.group_name}@{key}'

    def get_definition_code(self, add_at_env=False):
        # https://tex.stackexchange.com/questions/34312/how-to-create-a-command-with-key-values

        # build code
        code = TexCode()
        if add_at_env:
            code += self.at_env_code_start()

        if self.is_keyval_macro:
            # define keys
            for key, value in self.option_dict.items():
                code += f'\\define@key{{{self.group_name}}}{{{key}}}{{\\def{self.keyval_macro_name(key)}{{#1}}}}'

            # set default keys
            kv_list = ','.join([f'{key}={value}' for key, value in self.option_dict.items()])
            code += f'\\setkeys{{{self.group_name}}}{{{kv_list}}}'

            # define macro
            code += f'\\newcommand{{{self.macro_name}}}[{self._num_args + 1}][]{{%'
            code += f'\\setkeys{{{self.group_name}}}{{#1}}%'
            code += f'{self._content}%'
            code += '}%'

        else:
            # define macro
            code += f'\\newcommand{{{self.macro_name}}}[{self._num_args}]{{%'
            code += f'{self._content}%'
            code += '}%'

        if add_at_env:
            code += self.at_env_code_end()
        return code

    def get_execution_code(self, option_dict=None, *args):
        code = TexCode()
        if self.is_keyval_macro:
            if option_dict is None:
                option_dict = dict()
            code += f'{self.macro_name}' + '[' + ','.join(
                [f'{key}={value}' for key, value in option_dict.items()]) + ']' + ''.join(
                [f'{{{arg}}}' for arg in args])
        else:
            code += f'{self.macro_name}' + ''.join([f'{{{arg}}}' for arg in args])
        return code


class TikzCommandReg(TikzCommand):

    def __init__(self, name, num_args, option_dict, content):
        super().__init__(name, num_args, option_dict, content)

    def is_valid(self):
        return self.num_args == 3 and not self.is_keyval_macro

    def get_execution_code(self, option_dict, t_label, b_label, reg_caption):
        return super().get_execution_code(option_dict, t_label, b_label, reg_caption)


class TikzCommandBit(TikzCommand):

    def __init__(self, name, num_args, option_dict, content):
        super().__init__(name, num_args, option_dict, content)

    def is_valid(self):
        return self.num_args == 3

    def get_execution_code(self, option_dict, l_label, r_label, bit_caption):
        return super().get_execution_code(option_dict, l_label, r_label, bit_caption)


class TikzCommandGate(TikzCommand):

    def __init__(self, name, num_args, option_dict, content):
        super().__init__(name, num_args, option_dict, content)

    def is_valid(self):
        return self.num_args == 6

    def get_execution_code(self, option_dict, tl_label, tr_label, br_label, bl_label, gate_caption, gate_label):
        return super().get_execution_code(option_dict, tl_label, tr_label, br_label, bl_label, gate_caption, gate_label)


class TikzEngine(Engine):

    def __init__(self):
        super().__init__()
        self._layout = TikzCircuitGridLayout()

    @property
    def layout(self):
        return self._layout

    @classmethod
    def doc_code_start(cls):
        return TexCode('\\begin{document}', '\\begin{tikzpicture}')

    @classmethod
    def doc_code_end(cls):
        return TexCode('\\end{tikzpicture}', '\\end{document}')

    def _render(self, representation, style_dict, **kwargs):
        tex_file_dict = dict()
        for circuit_index, circuit in representation.circuits.circuit_dict.items():
            tex_file_dict[circuit_index] = TexFile(circuit.name, self.get_circuit_code(circuit))
        return tex_file_dict

    def _update_obj_dict_code(self, obj_dict, obj_name, ObjectCls, **kwargs):
        code = TexCode()
        if obj_name not in obj_dict:
            obj_dict[obj_name] = ObjectCls(obj_name, **kwargs)
            if not obj_dict[obj_name].is_valid():
                raise ValueError(f'invalid {ObjectCls}: {obj_name}')
            code += obj_dict[obj_name].get_definition_code()
        return code

    def _update_color_dict(self, color_dict, color_name, colormodel, colorcode):
        return self._update_obj_dict_code(color_dict, color_name, TikzColor, colormodel=colormodel, colorcode=colorcode)

    def _update_style_dict(self, style_dict, style_name, option_dict, flags):
        return self._update_obj_dict_code(style_dict, style_name, TikzStyle, option_dict=option_dict, flags=flags)

    def _update_cmd_dict(self, cmd_dict, cmd_name, ObjectCls, num_args, option_dict, content):
        return self._update_obj_dict_code(cmd_dict, cmd_name, ObjectCls, num_args=num_args, option_dict=option_dict,
                                          content=content)

    def _update_cmd_dict_from_collection(self, cmd_dict, collection_dict, ObjectCls):
        code = TexCode()
        for item_key, item in collection_dict.items():
            if hasattr(item.style, 'cmd'):
                cmd_name = item.style.cmd.name
                code += self._update_cmd_dict(cmd_dict, cmd_name, ObjectCls, item.style.cmd.num_args,
                                              item.style.cmd.options.as_dict, item.style.cmd.content)
        return code

    def _execute_cmd_from_cmd_dict(self, cmd_dict, cmd_name, pre_code, ObjectCls, *args):
        cmd = cmd_dict.get(cmd_name, None)
        if cmd is not None and type(cmd) is ObjectCls:
            code = TexCode()
            code += pre_code
            code += TexCode(cmd.get_execution_code(*args))
            return code
        return None

    def _compile_option_dict_for_cmd_dict(self, cmd_dict, cmd_name, option_dict):
        cmd = cmd_dict.get(cmd_name, None)
        effective_option_dict = dict()
        for key, value in option_dict.items():
            if cmd is not None and key in cmd.option_dict:
                effective_option_dict[key] = value
        return effective_option_dict

    def _build_qureg_option_dict(self):
        return dict()

    def _build_clreg_option_dict(self):
        return dict()

    def _build_qubit_option_dict(self):
        return dict()

    def _build_clbit_option_dict(self):
        option_dict = dict()
        key = 'n'
        option_dict[key] = len(self._layout.qubits_xy)
        return option_dict

    def _build_gate_option_dict(self, gate_index, row, x_from, x_to):
        option_dict = dict()
        y_dict = self._layout.gate_xy[gate_index].y_dict_qu
        for y_index, (qubit_index, y) in enumerate(y_dict.items()):
            label = self._layout.coordinate_label(row, x_from, y)
            key = f'q{chr(ord("a") + y_index)}l'  # qubit number y_index pos (x_from, y)
            option_dict[key] = label
            label = self._layout.coordinate_label(row, x_to, y)
            key = f'q{chr(ord("a") + y_index)}r'  # qubit number y_index pos (x_to, y)
            option_dict[key] = label
            label = f'{qubit_index}'
            key = f'q{chr(ord("a") + y_index)}c'  # qubit number y_index index (caption)
            option_dict[key] = label
        y_dict = self._layout.gate_xy[gate_index].y_dict_cl
        for y_index, (clbit_index, y) in enumerate(y_dict.items()):
            label = self._layout.coordinate_label(row, x_from, y)
            key = f'c{chr(ord("a") + y_index)}l'  # clbit number y_index pos (x_from, y)
            option_dict[key] = label
            label = self._layout.coordinate_label(row, x_to, y)
            key = f'c{chr(ord("a") + y_index)}r'  # clbit number y_index pos (x_to, y)
            option_dict[key] = label
            label = f'{clbit_index}'
            key = f'c{chr(ord("a") + y_index)}c'  # clbit number y_index index (caption)
            option_dict[key] = label
        return option_dict

    def get_circuit_code(self, circuit):
        code = TexCode()

        # preamble
        code += TikzPreamble(circuit.style.preamble).get_definition_code()
        code += ''

        # color definitions
        code += '% colors'
        color_dict = {}
        for color in circuit.style.colors:
            code += self._update_color_dict(color_dict, color.name, color.colormodel, color.colorcode)
        code += ''

        # style definitions
        code += '% styles'
        style_dict = {}
        for style in circuit.style.styles:
            code += self._update_style_dict(style_dict, style.name, style.options.as_dict, style.flags)
        code += ''

        # macro definitions
        code += '% commands'
        cmd_dict = {}
        code += TikzCommand.at_env_code_start()
        for cmd in circuit.style.cmds + [circuit.style.bg_cmd, circuit.style.fg_cmd]:
            code += self._update_cmd_dict(cmd_dict, cmd.name, TikzCommand, cmd.num_args, cmd.options.as_dict,
                                          cmd.content)
        code += self._update_cmd_dict_from_collection(cmd_dict, circuit.regs.qreg_dict, TikzCommandReg)
        code += self._update_cmd_dict_from_collection(cmd_dict, circuit.regs.creg_dict, TikzCommandReg)
        code += self._update_cmd_dict_from_collection(cmd_dict, circuit.bits.qubit_dict, TikzCommandBit)
        code += self._update_cmd_dict_from_collection(cmd_dict, circuit.bits.clbit_dict, TikzCommandBit)
        code += self._update_cmd_dict_from_collection(cmd_dict, circuit.gates.gate_dict, TikzCommandGate)
        code += TikzCommand.at_env_code_end()
        code += ''

        # start document
        code += self.doc_code_start()
        code += ''
        code.ind_inc()

        # define grid
        code += '% grid'
        self._layout.compile(circuit)
        code += self._layout.get_grid_code()
        code += ''

        # background
        ul_label = self._layout.coordinate_label(0, 0, 0)
        br_label = self._layout.coordinate_label(self._layout.num_rows - 1, self._layout.row_width - 1,
                                                 self._layout.row_height - 1)
        pre_code = f'% background'
        option_dict = dict()
        code += self._execute_cmd_from_cmd_dict(cmd_dict, circuit.style.bg_cmd.name, pre_code, TikzCommand, option_dict,
                                                ul_label, br_label)
        code += ''

        # define bits
        code += '% bits'
        x_from = 0
        x_to = self._layout.row_width - 1
        for row in range(self._layout.num_rows):
            for qubit_index, qubit in circuit.bits.qubit_dict.items():
                max_row = self._layout.qubits_xy[qubit_index].max_row
                max_x_from = self._layout.qubits_xy[qubit_index].max_x_from
                max_x_to = self._layout.qubits_xy[qubit_index].max_x_to
                y = self._layout.qubits_xy[qubit_index].y
                if row > max_row:
                    continue
                elif row == max_row:
                    effective_x_from = max_x_from
                    effective_x_to = max_x_to
                else:
                    effective_x_from = x_from
                    effective_x_to = x_to
                l_label = self._layout.coordinate_label(row, effective_x_from, y)
                r_label = self._layout.coordinate_label(row, effective_x_to, y)
                option_dict = self._compile_option_dict_for_cmd_dict(cmd_dict, qubit.style.cmd.name,
                                                                     self._build_qubit_option_dict())
                qubit_caption = str(qubit_index)
                pre_code = f'% qubit #{qubit_index} @ {row}'
                code += self._execute_cmd_from_cmd_dict(cmd_dict, qubit.style.cmd.name, pre_code, TikzCommandBit,
                                                        option_dict, l_label, r_label, qubit_caption)
            if circuit.style.merge_clbits:
                clbit_index = 0
                max_row = max(
                    [self._layout.clbits_xy[clbit_index].max_row for clbit_index in circuit.bits.clbit_dict.keys()])
                y = self._layout.clbits_xy[clbit_index].y
                if row < max_row:
                    effective_x_from = x_from
                    effective_x_to = x_to
                else:
                    effective_x_from = min(
                        [self._layout.clbits_xy[clbit_index].max_x_from for clbit_index in
                         circuit.bits.clbit_dict.keys() if
                         self._layout.clbits_xy[clbit_index].max_row == max_row])
                    effective_x_to = max(
                        [self._layout.clbits_xy[clbit_index].max_x_to for clbit_index in
                         circuit.bits.clbit_dict.keys() if
                         self._layout.clbits_xy[clbit_index].max_row == max_row])

                l_label = self._layout.coordinate_label(row, effective_x_from, y)
                r_label = self._layout.coordinate_label(row, effective_x_to, y)
                option_dict = self._compile_option_dict_for_cmd_dict(cmd_dict, circuit.bits.clbit_dict[
                    clbit_index].style.cmd.name,
                                                                     self._build_clbit_option_dict())
                clbit_caption = 'clbits'
                pre_code = f'% {clbit_caption} @ {row}'
                code += self._execute_cmd_from_cmd_dict(cmd_dict, circuit.bits.clbit_dict[clbit_index].style.cmd.name,
                                                        pre_code, TikzCommandBit,
                                                        option_dict, l_label, r_label, clbit_caption)

            else:
                for clbit_index, clbit in circuit.bits.clbit_dict.items():
                    max_row = self._layout.clbits_xy[clbit_index].max_row
                    max_x_from = self._layout.clbits_xy[clbit_index].max_x_from
                    max_x_to = self._layout.clbits_xy[clbit_index].max_x_to
                    y = self._layout.clbits_xy[clbit_index].y
                    if row > max_row:
                        continue
                    elif row == max_row:
                        effective_x_from = max_x_from
                        effective_x_to = max_x_to
                    else:
                        effective_x_from = x_from
                        effective_x_to = x_to
                    l_label = self._layout.coordinate_label(row, effective_x_from, y)
                    r_label = self._layout.coordinate_label(row, effective_x_to, y)
                    option_dict = self._compile_option_dict_for_cmd_dict(cmd_dict, clbit.style.cmd.name,
                                                                         self._build_clbit_option_dict())
                    clbit_caption = str(clbit_index)
                    pre_code = f'% clbit #{clbit_index} @ {row}'
                    code += self._execute_cmd_from_cmd_dict(cmd_dict, clbit.style.cmd.name, pre_code, TikzCommandBit,
                                                            option_dict, l_label, r_label, clbit_caption)
            code += ''

            # define regs
            code += '% bits'
            for qureg_index, qureg in circuit.regs.qreg_dict.items():
                qubit_y = [self._layout.qubits_xy[qubit_index].y for qubit_index in qureg.bit_index_dict.values()]
                y_from = min(qubit_y)
                y_to = max(qubit_y)
                t_label = self._layout.coordinate_label(row, x_from, y_from)
                b_label = self._layout.coordinate_label(row, x_from, y_to)
                option_dict = self._compile_option_dict_for_cmd_dict(cmd_dict, qureg.style.cmd.name,
                                                                     self._build_qureg_option_dict())
                qreg_caption = str(qureg_index)
                pre_code = f'% qureg #{qureg_index} @ {row}'
                code += self._execute_cmd_from_cmd_dict(cmd_dict, qureg.style.cmd.name, pre_code, TikzCommandReg,
                                                        option_dict, t_label, b_label, qreg_caption)
            for clreg_index, clreg in circuit.regs.creg_dict.items():
                clbit_y = [self._layout.clbits_xy[clbit_index].y for clbit_index in clreg.bit_index_dict.values()]
                y_from = min(clbit_y)
                y_to = max(clbit_y)
                t_label = self._layout.coordinate_label(row, x_from, y_from)
                b_label = self._layout.coordinate_label(row, x_from, y_to)
                option_dict = self._compile_option_dict_for_cmd_dict(cmd_dict, clreg.style.cmd.name,
                                                                     self._build_clreg_option_dict())
                creg_caption = str(clreg_index)
                pre_code = f'% clreg #{clreg_index} @ {row}'
                code += self._execute_cmd_from_cmd_dict(cmd_dict, clreg.style.cmd.name, pre_code, TikzCommandReg,
                                                        option_dict, t_label, b_label, creg_caption)
        code += ''

        # define gates
        code += '% gates'
        for gate_index, gate in circuit.gates.gate_dict.items():
            if not gate.style.cmd.name in cmd_dict:
                continue

            # arguments
            row = self._layout.gate_xy[gate_index].row
            x_from = self._layout.gate_xy[gate_index].x_from
            x_to = self._layout.gate_xy[gate_index].x_to
            y_from = self._layout.gate_xy[gate_index].y_from
            y_to = self._layout.gate_xy[gate_index].y_to
            bl_label = self._layout.coordinate_label(row, x_from, y_to)
            br_label = self._layout.coordinate_label(row, x_to, y_to)
            tr_label = self._layout.coordinate_label(row, x_to, y_from)
            tl_label = self._layout.coordinate_label(row, x_from, y_from)
            gate_label = f'gate{gate_index}'

            # automatically generated options
            option_dict = self._compile_option_dict_for_cmd_dict(cmd_dict, gate.style.cmd.name,
                                                                 self._build_gate_option_dict(gate_index, row, x_from,
                                                                                              x_to))

            # build code
            gate_caption = str(gate.label)
            pre_code = f'% gate #{gate_index}: {gate.name} (Q:{gate.qubit_indices}|C:{gate.clbit_indices}) @ {row} ({x_from}-{x_to}/{y_from}-{y_to})'
            code += self._execute_cmd_from_cmd_dict(cmd_dict, gate.style.cmd.name, pre_code, TikzCommandGate,
                                                    option_dict, tl_label, tr_label, br_label, bl_label, gate_caption,
                                                    gate_label)
        code += ''

        # foreground
        ul_label = self._layout.coordinate_label(0, 0, 0)
        br_label = self._layout.coordinate_label(self._layout.num_rows - 1, self._layout.row_width - 1,
                                                 self._layout.row_height - 1)
        pre_code = f'% foreground'
        option_dict = dict()
        code += self._execute_cmd_from_cmd_dict(cmd_dict, circuit.style.fg_cmd.name, pre_code, TikzCommand, option_dict,
                                                ul_label, br_label)
        code += ''

        # end document
        code.ind_dec()
        code += self.doc_code_end()

        return code
