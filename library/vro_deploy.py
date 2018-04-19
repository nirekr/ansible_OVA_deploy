from pyVmomi import vim, vmodl
import requests

def find_virtual_machine(content, searched_vm_name):
    virtual_machines = get_all_objs(content, [vim.VirtualMachine])
    for vm in virtual_machines:
        if vm.name == searched_vm_name:
            return vm
    return None

def get_all_objs(content, vimtype):
    obj = {}
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for managed_object_ref in container.view:
        obj.update({managed_object_ref: managed_object_ref.name})
    return obj

def connect_to_api(vchost, vc_user, vc_pwd):
    service_instance = SmartConnect(host=vchost, user=vc_user, pwd=vc_pwd)
    return service_instance.RetrieveContent()

def main():
    module = AnsibleModule(
        argument_spec=dict(
            ovftool_path=dict(required=True, type='str'),
            datacenter=dict(required=True, type='str'),
            datastore=dict(required=True, type='str'),
            portgroup=dict(required=True, type='str'),
            cluster=dict(required=True, type='str'),
            vmname=dict(required=True, type='str'),
            #hostname=dict(required=True, type='str'),
            dns_server=dict(required=True, type='str'),
            #dns_domain=dict(required=True, type='str'),
            gateway=dict(required=True, type='str'),
            ip_address=dict(required=True, type='str'),
            netmask=dict(required=True, type='str'),
            admin_password=dict(required=True, type='str', no_log=True),
            ssh_enable=dict(required=True, type='str'),
            path_to_ova=dict(required=True, type='str'),
            ova_file=dict(required=True, type='str'),
            disk_mode=dict(default='thin'),
            vcenter=dict(required=True, type='str'),
            vcenter_user=dict(required=True, type='str'),
            vcenter_passwd=dict(required=True, type='str', no_log=True)
        ),
        supports_check_mode=True
    )
     ovftool_exec = '{}/ovftool'.format(module.params['ovftool_path'])
    ova_file = '{}/{}'.format(module.params['path_to_ova'], module.params['ova_file'])
    vi_string = 'vi://lab%5Cnirekr1:{}@{}/{}/host/{}/'.format(
                                                   module.params['vcenter_passwd'], module.params['vcenter'],
                                                   module.params['datacenter'], module.params['cluster'])

    ova_tool_result = module.run_command([ovftool_exec,
                                          '--acceptAllEulas',
                                          '--skipManifestCheck',
                                          '--powerOn',
                                          '--noSSLVerify',
                                          '--allowExtraConfig',
                                          '--diskMode={}'.format(module.params['disk_mode']),
                                          '--datastore={}'.format(module.params['datastore']),
                                          '--network={}'.format(module.params['portgroup']),
                                          '--name={}'.format(module.params['vmname']),
                                          '--prop:varoot-password={}'.format(module.params['admin_password']),
                                          '--prop:vcoconf-password={}'.format(module.params['admin_password']),
                                          '--prop:va-ssh-enabled={}'.format(module.params['ssh_enable']),
                                          #'--prop:vami.hostname={}'.format(module.params['hostname']),
                                          '--prop:vami.gateway.VMware_vRealize_Orchestrator_Appliance={}'.format(module.params['gateway']),
                                          #'--prop:vami.domain.VMware_vRealize_Orchestrator_Appliance={}'.format(module.params['dns_domain']),
                                          '--prop:vami.DNS.VMware_vRealize_Orchestrator_Appliance={}'.format(module.params['dns_server']),
                                          '--prop:vami.ip0.VMware_vRealize_Orchestrator_Appliance={}'.format(module.params['ip_address']),
                                          '--prop:vami.netmask0.VMware_vRealize_Orchestrator_Appliance={}'.format(module.params['netmask']),
                                          #'vi://{{ vcenter_user }}:{{ vcenter_passwd }}@{{ vcenter }}:443/{{ datacenter }}/host/{{ cluster }}',
                                          ova_file,
                                          vi_string])

    if ova_tool_result[0] != 0:
        module.fail_json(msg='Failed to deploy OVA, error message from ovftool is: {}'.format(ova_tool_result[1]))

    module.exit_json(changed=True, ova_tool_result=ova_tool_result)
    if not IMPORTS:
        module.fail_json(msg="Failed to import modules")

    content = connect_to_api(module)

    vro_vm = find_virtual_machine(content, module.params['vmname'])

from ansible.module_utils.basic import *
from ansible.module_utils.vmware import *

if __name__ == '__main__':
   main()
