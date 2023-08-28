from abc import abstractmethod


class Engine:

    def __init__(self):
        super().__init__()

    @abstractmethod
    def _render(self, representation, style_dict, **kwargs):
        raise NotImplementedError

    def _representation_preprocessing(self, representation, style_dict):
        representation.reset_style()
        representation.update_style(**style_dict)

    def _representation_postprocessing(self, representation):
        representation.reset_style()

    def _result_postprocessing(self, result, post_action):
        if callable(post_action):
            result = post_action(result)
        return result

    def render(self, representation, style_dict, post_action=None, **kwargs):
        self._representation_preprocessing(representation, style_dict)
        result = self._render(representation, style_dict, **kwargs)
        self._representation_postprocessing(representation)
        return self._result_postprocessing(result, post_action)
