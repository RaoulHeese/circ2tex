import json
from types import SimpleNamespace


class ItemDict:
    # item dictionaries of the form item index: item object
    def __init__(self):
        self._item_dict = {}

    def __getitem__(self, key):
        return self._item_dict[key]

    def __iter__(self):
        return self.values()

    def keys(self):
        return sorted(self._item_dict.keys())

    def items(self):
        return ((key, self._item_dict[key]) for key in self.keys())

    def values(self):
        return (self._item_dict[key] for key in self.keys())

    def add_item(self, item, index=None):
        assert item not in self._item_dict.values()
        if index is not None:
            assert index not in self._item_dict
        else:
            index = len(self._item_dict)
        self._item_dict[index] = item
        return index


class Style(SimpleNamespace):

    def __init__(self, /, **kwargs):
        super().__init__()
        self._set(**kwargs)

    @property
    def as_dict(self):
        return self.__dict__

    @classmethod
    def _process_value(cls, value):
        if type(value) is dict:
            value = Style(**value)
        elif type(value) is list:
            value = [cls._process_value(value_element) for value_element in value]
        elif value == 'null':
            value = None
        return value

    def _set(self, **kwargs):
        for key, value in kwargs.items():
            self.__dict__.update({key: self._process_value(value)})

    def clear(self):
        self.__dict__.clear()

    def update(self, /, **kwargs):
        self._set(**kwargs)


class StyledObject:

    def __init__(self):
        self._style = Style()
        self._reset_style()

    @property
    def style(self):
        return self._style

    def _get_default_style_dict(self):
        return dict()

    def _reset_style(self):
        self._style.clear()
        self._style.update(**self._get_default_style_dict())

    def _update_style(self, **kwargs):
        self._style.update(**kwargs)

    def reset_style(self):
        self._reset_style()

    def update_style(self, **kwargs):
        self._update_style(**kwargs)


class StyleData:
    def __init__(self, input):
        self._style_collection_dict = self.get(input)

    @classmethod
    def get(cls, input):
        style_collection_dict = dict()
        if type(input) is str:
            style_collection_dict.update(**cls.load_style_data_from_file(input))
        elif type(input) is list:
            for input_part in input:
                style_collection_dict.update(**cls.get(input_part))
        elif type(input) is dict:
            style_collection_dict.update(**input)
        else:
            raise ValueError
        return style_collection_dict

    @classmethod
    def load_style_data_from_file(cls, path):
        with open(path, 'r') as fh:
            return json.load(fh)

    @property
    def style_collection_dict(self):
        return self._style_collection_dict

    @property
    def style_names(self):
        return list(self.style_collection_dict.keys())

    def style_dict(self, name):
        return self.style_collection_dict[name]
