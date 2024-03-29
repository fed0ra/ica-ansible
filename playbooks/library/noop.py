#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

def run_module():
    module_args = dict(
        noop=dict(type='list', required=True)
    )
    result = dict(
        changed=False
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
