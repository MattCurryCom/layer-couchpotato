#!/usr/bin/python3
import pytest
import mock

# TEMPLATE NOT IMPLEMENTED YET

# import sys
# import shutil
#
#
# @pytest.fixture
# def mock_layers():
#     sys.modules["charms.layer"] = mock.Mock()
#     sys.modules["reactive"] = mock.Mock()
#
#
# # @pytest.fixture
# # def mock_check_call(monkeypatch):
# #     mock_call = mock.Mock()
# #     monkeypatch.setattr('libdup.subprocess.check_call', mock_call)
# #     return mock_call
#
#
# @pytest.fixture
# def mock_hookenv_config(monkeypatch):
#     import yaml
#
#     def mock_config():
#         cfg = {}
#         yml = yaml.load(open('./config.yaml'))
#
#         # Load all defaults
#         for key, value in yml['options'].items():
#             cfg[key] = value['default']
#
#         return cfg
#
#     monkeypatch.setattr('libdup.hookenv.config', mock_config)
#
#
# @pytest.fixture
# def dh(tmpdir, mock_layers, mock_hookenv_config, monkeypatch):
#     from libdup import DuplicatiHelper
#     dh = DuplicatiHelper()
#
#     # Set correct charm_dir
#     monkeypatch.setattr('libdup.hookenv.charm_dir', lambda: '.')
#
#     # Patch the config file to a tmpfile
#     config_file = tmpdir.join("duplicati")
#     dh.config_file = config_file.strpath
#
#     # Copy example config into tmp location
#     shutil.copyfile('./tests/unit/duplicati', dh.config_file)
#
#     # Any other functions that load DH will get this version
#     monkeypatch.setattr('libdup.DuplicatiHelper', lambda: dh)
#
#     return dh
