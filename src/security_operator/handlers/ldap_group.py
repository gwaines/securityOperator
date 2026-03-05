"""Handler for LocalLdapGroup CRD."""

import kopf
import logging
from typing import Dict, Any
from security_operator.utils.ldap_client import LdapClient
from security_operator.models.ldap_group import LocalLdapGroup

logger = logging.getLogger(__name__)


@kopf.on.create('starlingx.io', 'v1', 'localldapgroups')
async def create_ldap_group(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """Handle creation of LocalLdapGroup."""
    logger.info(f"Creating LDAP group: {name} in namespace: {namespace}")
    
    group = LocalLdapGroup.from_spec(spec, name, namespace)
    ldap_client = LdapClient()
    
    try:
        gid_number = await ldap_client.create_group(group)
        return {'gidNumber': gid_number}
    except Exception as e:
        logger.error(f"Failed to create LDAP group {name}: {e}")
        raise kopf.PermanentError(f"Failed to create LDAP group: {e}")


@kopf.on.update('starlingx.io', 'v1', 'localldapgroups')
async def update_ldap_group(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """Handle update of LocalLdapGroup."""
    logger.info(f"Updating LDAP group: {name} in namespace: {namespace}")
    
    group = LocalLdapGroup.from_spec(spec, name, namespace)
    ldap_client = LdapClient()
    
    try:
        await ldap_client.update_group(group)
        return {'updated': True}
    except Exception as e:
        logger.error(f"Failed to update LDAP group {name}: {e}")
        raise kopf.PermanentError(f"Failed to update LDAP group: {e}")


@kopf.on.delete('starlingx.io', 'v1', 'localldapgroups')
async def delete_ldap_group(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """Handle deletion of LocalLdapGroup."""
    logger.info(f"Deleting LDAP group: {name} in namespace: {namespace}")
    
    ldap_client = LdapClient()
    
    try:
        await ldap_client.delete_group(name)
        logger.info(f"Successfully deleted LDAP group: {name}")
    except Exception as e:
        logger.error(f"Failed to delete LDAP group {name}: {e}")
        raise kopf.PermanentError(f"Failed to delete LDAP group: {e}")