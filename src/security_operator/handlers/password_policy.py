"""Handler for LocalLdapPasswordPolicy CRD."""

import kopf
import logging
from typing import Dict, Any
from security_operator.utils.ldap_client import LdapClient
from security_operator.models.password_policy import LocalLdapPasswordPolicy

logger = logging.getLogger(__name__)


@kopf.on.create('starlingx.io', 'v1', 'localldappasswordpolicies')
async def create_password_policy(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """Handle creation of LocalLdapPasswordPolicy."""
    logger.info(f"Creating password policy: {name} in namespace: {namespace}")
    
    policy = LocalLdapPasswordPolicy.from_spec(spec, name, namespace)
    ldap_client = LdapClient()
    
    try:
        await ldap_client.create_password_policy(policy)
        return {'created': True}
    except Exception as e:
        logger.error(f"Failed to create password policy {name}: {e}")
        raise kopf.PermanentError(f"Failed to create password policy: {e}")


@kopf.on.update('starlingx.io', 'v1', 'localldappasswordpolicies')
async def update_password_policy(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """Handle update of LocalLdapPasswordPolicy."""
    logger.info(f"Updating password policy: {name} in namespace: {namespace}")
    
    policy = LocalLdapPasswordPolicy.from_spec(spec, name, namespace)
    ldap_client = LdapClient()
    
    try:
        await ldap_client.update_password_policy(policy)
        return {'updated': True}
    except Exception as e:
        logger.error(f"Failed to update password policy {name}: {e}")
        raise kopf.PermanentError(f"Failed to update password policy: {e}")


@kopf.on.delete('starlingx.io', 'v1', 'localldappasswordpolicies')
async def delete_password_policy(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """Handle deletion of LocalLdapPasswordPolicy."""
    logger.info(f"Deleting password policy: {name} in namespace: {namespace}")
    
    ldap_client = LdapClient()
    
    try:
        await ldap_client.delete_password_policy(name)
        logger.info(f"Successfully deleted password policy: {name}")
    except Exception as e:
        logger.error(f"Failed to delete password policy {name}: {e}")
        raise kopf.PermanentError(f"Failed to delete password policy: {e}")