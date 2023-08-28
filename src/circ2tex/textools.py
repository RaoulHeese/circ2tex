import os
from abc import abstractmethod


class TexObject:

    def __init__(self):
        pass


class TexIndentedCodeObject(TexObject):

    def __init__(self, indent=0):
        super().__init__()
        self.indent = indent

    @property
    def indent(self):
        return self._indent

    @indent.setter
    def indent(self, value):
        self._indent = value
        if self._indent < 0:
            self._indent = 0

    def ind_inc(self):
        self.indent += 1

    def ind_dec(self):
        self.indent -= 1


class TexCodeLine(TexIndentedCodeObject):
    def __init__(self, content, indent=0):
        super().__init__(indent)
        self.content = content

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    def __repr__(self):
        if self.content is None:
            return ''
        return '\t' * self.indent + str(self.content)


class TexCode(TexIndentedCodeObject):

    def __init__(self, content=None, *args):
        super().__init__(0)
        self._lines = []
        self.add(content)
        for arg in args:
            self.add(arg)

    def __iter__(self):
        for line in self._lines:
            yield line

    def __add__(self, other):
        self.add(other)

    def __iadd__(self, other):
        self.add(other)
        return self

    def __repr__(self):
        return '\n'.join(repr(line) for line in self)

    def add(self, content, indent=0):
        if content is None:
            return
        elif type(content) is TexCode:
            for line in content:
                self.add(line)
        elif type(content) is TexCodeLine:
            self.add(content.content, content.indent)
        elif type(content) is str:
            self._lines.append(TexCodeLine(content=content, indent=self.indent + indent))
        else:
            raise ValueError

    def clear(self):
        self._lines.clear()


class TexFile(TexObject):

    def __init__(self, name, content=None):
        super().__init__()
        self._name = name
        self._code = TexCode(content)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def code(self):
        return self._code

    def save(self, file_dir='', overwrite_file_name=None):
        if overwrite_file_name is None:
            file_name = self.name
        else:
            file_name = overwrite_file_name
        if not file_name.endswith('.tex'):
            file_name += '.tex'
        file_path = os.path.join(file_dir, file_name)
        with open(file_path, 'w') as fh:
            fh.write(repr(self.code))
        return file_path


class TexCompiler:
    def __init__(self, compiler):
        self._compiler = compiler

    @abstractmethod
    def _get_cmd_str(self, file_path, option_dict):
        raise NotImplementedError

    def _save_to_file(self, tex_file, file_dir, overwrite_file_name):
        return tex_file.save(file_dir, overwrite_file_name)

    def _compile(self, file_path, option_dict):
        cmd_str = self._get_cmd_str(file_path, option_dict)
        os.system(cmd_str)

    def compile(self, tex_file, file_dir='', overwrite_file_name=None, option_dict=None):
        file_path = self._save_to_file(tex_file, file_dir, overwrite_file_name)
        self._compile(file_path, option_dict)
        return tex_file

    def compile_collection(self, tex_file_dict, file_dir='', name_fun=lambda file_name: None, option_dict=None):
        for tex_file in tex_file_dict.values():
            self.compile(tex_file, file_dir, name_fun(tex_file.name), option_dict)
        return tex_file_dict


class LualatexCompiler(TexCompiler):
    output_directory_arg = '-output-directory'

    def __init__(self):
        super().__init__('lualatex')

    def _get_cmd_str(self, file_path, option_dict):
        if option_dict is None:
            option_dict = dict()
        file_dir = os.path.split(file_path)[0]
        return f'{self._compiler} {self.output_directory_arg}={file_dir} "{file_path}"'
