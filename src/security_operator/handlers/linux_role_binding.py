"""Handler for LinuxRoleBinding CRD."""

import kopf
import logging
from typing import Dict, Any
from security_operator.utils.linux_groups import LinuxGroupManager
from security_operator.models.linux_role_binding import LinuxRoleBinding

logger = logging.getLogger(__name__)


@kopf.on.create('starlingx.io', 'v1', 'linuxrolebindings')
async def create_linux_role_binding(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """Handle creation of LinuxRoleBinding."""
    logger.info(f"Creating Linux role binding: {name} in namespace: {namespace}")
    
    binding = LinuxRoleBinding.from_spec(spec, name, namespace)
    group_manager = LinuxGroupManager()
    
    try:
        await group_manager.create_role_binding(binding)
        return {'created': True}
    except Exception as e:
        logger.error(f"Failed to create Linux role binding {name}: {e}")
        raise kopf.PermanentError(f"Failed to create Linux role binding: {e}")


@kopf.on.update('starlingx.io', 'v1', 'linuxrolebindings')
async def update_linux_role_binding(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """Handle update of LinuxRoleBinding."""
    logger.info(f"Updating Linux role binding: {name} in namespace: {namespace}")
    
    binding = LinuxRoleBinding.from_spec(spec, name, namespace)
    group_manager = LinuxGroupManager()
    
    try:
        await group_manager.update_role_binding(binding)
        return {'updated': True}
    except Exception as e:
        logger.error(f"Failed to update Linux role binding {name}: {e}")
        raise kopf.PermanentError(f"Failed to update Linux role binding: {e}")


@kopf.on.delete('starlingx.io', 'v1', 'linuxrolebindings')
async def delete_linux_role_binding(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """Handle deletion of LinuxRoleBinding."""
    logger.info(f"Deleting Linux role binding: {name} in namespace: {namespace}")
    
    group_manager = LinuxGroupManager()
    
    try:
        await group_manager.delete_role_binding(name)
        logger.info(f"Successfully deleted Linux role binding: {name}")
    except Exception as e:
        logger.error(f"Failed to delete Linux role binding {name}: {e}")
        raise kopf.PermanentError(f"Failed to delete Linux role binding: {e}")