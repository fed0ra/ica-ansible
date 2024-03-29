#!/usr/bin/env python
# 一个简单的过滤器插件，发送警告消息，实现ansible自定义告警
# 将脚本放入：[playbook_dir]/filter_plugins/warn_custom.py
# 调用脚本示例剧本如下：ansible-playbook -i hosts playbooks/test-warn-custom.yaml
#---
#- name: Demonstrate warning filter plugin
#  gather_facts: no
#  hosts: all

#  tasks:
#    - meta: end_play
#      when: ('file XYZ cannot be processed' | warn_custom())
#      delegate_to: localhost
#      run_once: yes


from ansible.utils.display import Display


class FilterModule(object):
    """
    see: https://stackoverflow.com/a/56420339/4027379
    """
    def filters(self):
        return {'warn_custom': self.warn_filter}

    def warn_filter(self, message, **kwargs):
        Display().warning(message)
        return message
