# (c) Copyright 2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from neutron_lib import constants

from neutron.common import utils
from neutron import manager
from neutron.services.trunk.drivers.openvswitch import constants as ovs_const


def gen_trunk_br_name(trunk_id):
    return ((ovs_const.TRUNK_BR_PREFIX + trunk_id)
            [:constants.DEVICE_NAME_MAX_LEN - 1])


def are_agent_types_available_on_host(context, agent_types, host):
    """Return true if agent types are present on the host."""
    core_plugin = manager.NeutronManager.get_plugin()
    if utils.is_extension_supported(core_plugin, 'agent'):
        return bool(core_plugin.get_agents(
            context.elevated(),
            filters={'host': [host], 'agent_type': agent_types}))
    return False


def is_driver_compatible(context, driver, interface, binding_host):
    """Return true if the driver is compatible with the interface and host.

    There may be edge cases where a stale view or the deployment may make the
    following test fail to detect the right driver in charge of the bound port.
    """

    # NOTE(armax): this logic stems from the fact that the way Neutron is
    # architected we do not have a univocal mapping between VIF type and the
    # Driver serving it, in that the same vif type can be supported by
    # multiple drivers. A practical example of this is OVS and OVN in the
    # same deployment. In order to uniquely identify the driver, we cannot
    # simply look at the vif type, and we need to look at whether the host
    # to which the port is bound is actually managed by one driver or the
    # other.
    is_interface_compatible = driver.is_interface_compatible(interface)

    # For an agentless driver, only interface compatibility is required.
    if not driver.agent_type:
        return is_interface_compatible

    # For an agent-based driver, both interface and agent compat is required.
    return (
        is_interface_compatible and
        are_agent_types_available_on_host(
            context, [driver.agent_type], binding_host))
