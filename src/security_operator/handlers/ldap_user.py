"""Handler for LocalLdapUser CRD."""

import kopf
import logging
from typing import Dict, Any
from kubernetes import client, config
from security_operator.utils.ldap_client import LdapClient
from security_operator.models.ldap_user import LocalLdapUser

logger = logging.getLogger(__name__)

# Initialize Kubernetes client
try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()
k8s_client = client.CustomObjectsApi()


@kopf.on.create('starlingx.io', 'v1', 'localldapusers')
async def create_ldap_user(spec: Dict[str, Any], name: str, namespace: str, labels: Dict[str, str], patch: kopf.Patch, **kwargs):
    """Handle creation of LocalLdapUser."""
    logger.info(f"Creating LDAP user: {name} in namespace: {namespace}")
    
    patch.status['gidNumber'] = 100
    patch.status['temporaryLockOut'] = False

    if labels.get('imported') == 'true':
        logger.info(f"Skipping LDAP creation for imported user: {name}")
        return

    user = LocalLdapUser.from_spec(spec, name, namespace)
    ldap_client = LdapClient()
    
    try:
        uid_number = await ldap_client.create_user(user)
        patch.status['uidNumber'] = uid_number
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
    
    # Remove user from all groups first
    await _remove_user_from_all_groups(name, namespace)
    
    ldap_client = LdapClient()
    
    try:
        await ldap_client.delete_user(name)
        logger.info(f"Successfully deleted LDAP user: {name}")
    except Exception as e:
        logger.error(f"Failed to delete LDAP user {name}: {e}")
        raise kopf.PermanentError(f"Failed to delete LDAP user: {e}")


async def _remove_user_from_all_groups(user_name: str, namespace: str):
    """Remove user from all groups that contain them."""
    try:
        # Get all groups in the namespace
        groups = k8s_client.list_namespaced_custom_object(
            group='starlingx.io',
            version='v1',
            namespace=namespace,
            plural='localldapgroups'
        )
        
        for group in groups['items']:
            group_name = group['metadata']['name']
            members = group['spec'].get('members', [])
            
            # Check if user is in this group
            updated_members = [
                member for member in members 
                if not (member.get('kind') == 'LocalLdapUser' and member.get('name') == user_name)
            ]
            
            # Update group if user was removed
            if len(updated_members) != len(members):
                logger.info(f"Removing user {user_name} from group {group_name}")
                
                # Patch the group to remove the user
                patch_body = {
                    'spec': {
                        'members': updated_members
                    }
                }
                
                k8s_client.patch_namespaced_custom_object(
                    group='starlingx.io',
                    version='v1',
                    namespace=namespace,
                    plural='localldapgroups',
                    name=group_name,
                    body=patch_body
                )
                
                logger.info(f"Successfully removed user {user_name} from group {group_name}")
    
    except Exception as e:
        logger.error(f"Failed to remove user {user_name} from groups: {e}")
        # Don't raise - we still want to delete the user even if group cleanup fails