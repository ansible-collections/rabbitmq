#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2013, Chatham Financial <oss@chathamfinancial.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: rabbitmq_user_limits
short_description: Manage RabbitMQ user limits
description:
  - Manage the state of user limits in RabbitMQ
author: Aitor Pazos (@aitorpazos)
options:
  user:
    description:
      - Name of user to manage limits for
    type: str
    required: true
    aliases: [username, name]
  max_connections:
      description:
          - Max number of concurrent client connections.
          - Negative value means "no limit".
          - Ignored when the I(state) is C(absent).
      type: int
      default: -1
  max_channels:
      description:
          - Max number of channels.
          - Negative value means "no limit".
          - Ignored when the I(state) is C(absent).
      type: int
      default: -1
  node:
      description:
          - Name of the RabbitMQ Erlang node to manage.
      type: str
  state:
      description:
          - Specify whether the limits are to be set or cleared.
          - If set to C(absent), the limits of both I(max_connections) and I(max_channels) will be cleared.
      type: str
      default: present
      choices: [present, absent]
'''

EXAMPLES = '''
# Limit both of the max number of connections and channels on the user 'guest'.
- community.rabbitmq.rabbitmq_user_limits:
    user: guest
    max_connections: 64
    max_channels: 256
    state: present

# Limit the max number of connections on the user 'guest'.
# This task implicitly clears the max number of channels limit using default value: -1.
- community.rabbitmq.rabbitmq_user_limits:
    user: guest
    max_connections: 64
    state: present

# Clear the limits on the user 'guest'.
- community.rabbitmq.rabbitmq_user_limits:
    user: guest
    state: absent
'''

RETURN = ''' # '''

import json
from ansible.module_utils.basic import AnsibleModule


class RabbitMqUserLimits(object):
  def __init__(self, module):
    self._module = module
    self._max_connections = module.params['max_connections']
    self._max_channels = module.params['max_channels']
    self._node = module.params['node']
    self._state = module.params['state']
    self._user = module.params['user']
    self._rabbitmqctl = module.get_bin_path('rabbitmqctl', True)

  def _exec(self, args):
    cmd = [self._rabbitmqctl, '-q']
    if self._node is not None:
      cmd.extend(['-n', self._node])
    rc, out, err = self._module.run_command(cmd + args, check_rc=True)
    return dict(rc=rc, out=out.splitlines(), err=err.splitlines())

  def list(self):
    exec_result = self._exec(['list_user_limits', '--user', self._user])
    user_limits = exec_result['out'][0]
    max_connections = None
    max_channels = None
    if user_limits:
      user_limits = json.loads(user_limits)
      if 'max-connections' in user_limits:
        max_connections = user_limits['max-connections']
      if 'max-channels' in user_limits:
        max_channels = user_limits['max-channels']
    return dict(
      max_connections=max_connections,
      max_channels=max_channels
    )

  def set(self):
    if self._module.check_mode:
      return

    if self._max_connections != -1:
      json_str = '{{"max-connections": {0}}}'.format(self._max_connections)
      self._exec(['set_user_limits', self._user, json_str])
    else:
      self._exec('clear_user_limits', self._user, "max-connections")

    if self._max_channels != -1:
      json_str = '{{"max-channels": {0}}}'.format(self._max_channels)
      self._exec(['set_user_limits', self._user, json_str])
    else:
      self._exec('clear_user_limits', self._user, "max-channels")

  def clear(self):
    if self._module.check_mode:
      return
    self._exec(['clear_user_limits', self._user, 'all'])


def main():
  arg_spec = dict(
    max_connections=dict(default=-1, type='int'),
    max_channels=dict(default=-1, type='int'),
    node=dict(default=None, type='str'),
    state=dict(default='present', choices=['present', 'absent'], type='str'),
    user=dict(default='guest', type='str')
  )

  module = AnsibleModule(
    argument_spec=arg_spec,
    supports_check_mode=True
  )

  if self._version and self._version < Version('3.8.10'):
    module.fail_json(changed=False,
                     msg="User limits are only available for RabbitMQ >= 3.8.10. Detected version: %s" % self._version)

  max_connections = module.params['max_connections']
  max_channels = module.params['max_channels']
  node = module.params['node']
  state = module.params['state']
  user = module.params['user']

  module_result = dict(changed=False)
  rabbitmq_user_limits = RabbitMqUserLimits(module)
  current_status = rabbitmq_user_limits.list()

  if state == 'present':
    wanted_status = dict(
      max_connections=max_connections,
      max_channels=max_channels
    )
  else:  # state == 'absent'
    wanted_status = dict(
      max_connections=None,
      max_channels=None
    )

  if current_status != wanted_status:
    module_result['changed'] = True
    if state == 'present':
      rabbitmq_user_limits.set()
    else:  # state == 'absent'
      rabbitmq_user_limits.clear()

  module.exit_json(**module_result)


if __name__ == '__main__':
  main()
