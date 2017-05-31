# Copyright 2017 PerfKitBenchmarker Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for _ManagedRelationalDbSpec"""

import contextlib
import mock
import re
import unittest

from perfkitbenchmarker import benchmark_spec
from perfkitbenchmarker import context
from perfkitbenchmarker import errors
from perfkitbenchmarker import os_types
from perfkitbenchmarker import providers
from perfkitbenchmarker import vm_util
from perfkitbenchmarker.configs import benchmark_config_spec
from perfkitbenchmarker.providers.gcp import gce_virtual_machine
from tests import mock_flags


_BENCHMARK_NAME = 'name'
_BENCHMARK_UID = 'benchmark_uid'
_COMPONENT = 'test_component'
_FLAGS = None


def _mergeDicts(dict1, dict2):
  result = dict1.copy()
  result.update(dict2)
  return result

class ManagedRelationalDbSpecTestCase(unittest.TestCase):

  def setUp(self):
    self.flags = mock_flags.MockFlags()
    self.flags['run_uri'].parse('123')

    self.minimal_spec = {
      'cloud': 'GCP',
      'database': 'mysql',
      'vm_spec': {
        'GCP': {
            'machine_type': 'n1-standard-1'
        }
      }
    }

  def testMinimalConfig(self):
    result = benchmark_config_spec._ManagedRelationalDbSpec(
        _COMPONENT,
        flag_values = self.flags,
        **self.minimal_spec)
    self.assertEqual(result.database, 'mysql')
    self.assertEqual(result.cloud, 'GCP')
    self.assertIsInstance(result.vm_spec, gce_virtual_machine.GceVmSpec)

  def testDefaultDatabaseName(self):
    result = benchmark_config_spec._ManagedRelationalDbSpec(
        _COMPONENT,
        flag_values = self.flags,
        **self.minimal_spec)
    self.assertEqual(result.database_name, 'pkb-db-123')

  def testCustomDatabaseName(self):
    spec = _mergeDicts(self.minimal_spec, {
        'database_name': 'fakename'
    })
    result = benchmark_config_spec._ManagedRelationalDbSpec(
        _COMPONENT,
        flag_values = self.flags,
        **spec)
    self.assertEqual(result.database_name, 'fakename')

  def testDefaultDatabaseVersion(self):
    result = benchmark_config_spec._ManagedRelationalDbSpec(
        _COMPONENT,
        flag_values = self.flags,
        **self.minimal_spec)
    self.assertEqual(result.database_version, '5.6')

  def testCustomDatabaseVersion(self):
    spec = _mergeDicts(self.minimal_spec, {
        'database_version': '6.6'
    })
    result = benchmark_config_spec._ManagedRelationalDbSpec(
        _COMPONENT,
        flag_values = self.flags,
        **spec)
    self.assertEqual(result.database_version, '6.6')

  def testDefaultDatabasePassword(self):
    result = benchmark_config_spec._ManagedRelationalDbSpec(
        _COMPONENT,
        flag_values = self.flags,
        **self.minimal_spec)
    self.assertIsInstance(result.database_password, str)
    self.assertTrue(len(result.database_password) == 10)

  def testRandomDatabasePassword(self):
    spec = _mergeDicts(self.minimal_spec, {
        'database_password': 'fakepassword'
    })
    result = benchmark_config_spec._ManagedRelationalDbSpec(
        _COMPONENT,
        flag_values = self.flags,
        **spec)
    self.assertEqual(result.database_password, 'fakepassword')


class ManagedRelationalDbFlagsTestCase(unittest.TestCase):

  def setUp(self):
    self.flags = mock_flags.MockFlags()
    self.flags['run_uri'].parse('123')

    self.full_spec = {
      'cloud': 'GCP',
      'database': 'mysql',
      'database_name': 'fake_name',
      'database_password': 'fake_password',
      'vm_spec': {
        'GCP': {
            'machine_type': 'n1-standard-1'
        }
      }
    }

  # Not testing this yet, because it requires the implementation
  # of a managed_relational_db provider for the specified
  # cloud (other than GCP). We could mock it perhaps.
  def testCloudFlag(self):
    pass

  def testDatabaseFlag(self):
    self.flags['database'].parse('postgres')
    result = benchmark_config_spec._ManagedRelationalDbSpec(
        _COMPONENT,
        flag_values = self.flags,
        **self.full_spec)
    self.assertEqual(result.database, 'postgres')

  def testDatabaseNameFlag(self):
    self.flags['database_name'].parse('fakedbname')
    result = benchmark_config_spec._ManagedRelationalDbSpec(
        _COMPONENT,
        flag_values = self.flags,
        **self.full_spec)
    self.assertEqual(result.database_name, 'fakedbname')

  def testDatabasePasswordFlag(self):
    self.flags['database_password'].parse('fakepassword')
    result = benchmark_config_spec._ManagedRelationalDbSpec(
        _COMPONENT,
        flag_values = self.flags,
        **self.full_spec)
    self.assertEqual(result.database_password, 'fakepassword')


if __name__ == '__main__':
  unittest.main()