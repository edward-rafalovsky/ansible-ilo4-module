import pytest
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes
import json

def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)

class TestIloUser:
    def test_user_creation(self, mocker):
        # TODO: Implement tests
        pass

    def test_user_deletion(self, mocker):
        # TODO: Implement tests
        pass

    def test_user_privileges(self, mocker):
        # TODO: Implement tests
        pass 