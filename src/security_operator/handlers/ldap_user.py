"""Handler for LocalLdapUser CRD."""

import kopf
import logging
from typing import Dict, Any
from security_operator.utils.ldap_client import LdapClient
from security_operator.models.ldap_user import LocalLdapUser

logger = logging.getLogger(__name__)


@kopf.on.create('starlingx.io', 'v1', 'localldapusers')
async def create_ldap_user(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """Handle creation of LocalLdapUser."""
    logger.info(f"Creating LDAP user: {name} in namespace: {namespace}")
    
    user = LocalLdapUser.from_spec(spec, name, namespace)
    ldap_client = LdapClient()
    
    try:
        uid_number = await ldap_client.create_user(user)
        return {'uidNumber': uid_number, 'gidNumber': 100, 'temporaryLockOut': False}
    except Exception as e:
        logger.error(f"Failed to create LDAP user {name}: {e}")
        raise kopf.PermanentError(f"Failed to create LDAP user: {e}")


@kopf.on.update('starlingx.io', 'v1', 'localldapusers')
async def update_ldap_user(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """Handle update of LocalLdapUser."""
    logger.info(f"Updating LDAP user: {name} in namespace: {namespace}")
    
    user = LocalLdapUser.from_spec(spec, name, namespace)
    ldap_client = LdapClient()
    
    try:
        await ldap_client.update_user(user)
        return {'updated': True}
    except Exception as e:
        logger.error(f"Failed to update LDAP user {name}: {e}")
        raise kopf.PermanentError(f"Failed to update LDAP user: {e}")


@kopf.on.delete('starlingx.io', 'v1', 'localldapusers')
async def delete_ldap_user(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """Handle deletion of LocalLdapUser."""
    logger.info(f"Deleting LDAP user: {name} in namespace: {namespace}")
    
    ldap_client = LdapClient()
    
    try:
        await ldap_client.delete_user(name)
        logger.info(f"Successfully deleted LDAP user: {name}")
    except Exception as e:
        logger.error(f"Failed to delete LDAP user {name}: {e}")
        raise kopf.PermanentError(f"Failed to delete LDAP user: {e}")