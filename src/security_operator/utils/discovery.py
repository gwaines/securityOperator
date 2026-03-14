"""Discovery service for importing existing LDAP entries."""

import logging
import asyncio
from kubernetes import client, config
from security_operator.utils.ldap_client import LdapClient

logger = logging.getLogger(__name__)


class LdapDiscoveryService:
    """Service to discover and import existing LDAP entries as CRs."""
    
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.ldap_client = LdapClient()
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()
        self.k8s_client = client.CustomObjectsApi()
    
    async def discover_and_import(self):
        """Discover existing LDAP entries and create corresponding CRs."""
        logger.info("Starting LDAP discovery and import process")
        
        try:
            await self._import_users()
            await self._import_groups()
            logger.info("LDAP discovery and import completed successfully")
        except Exception as e:
            logger.error(f"LDAP discovery failed: {e}")
    
    async def _import_users(self):
        """Import existing LDAP users as LocalLdapUser CRs."""
        users = await self.ldap_client.discover_users()
        
        for user_data in users:
            cr_name = user_data['uid']
            
            # Check if CR already exists
            if await self._cr_exists('localldapusers', cr_name):
                logger.debug(f"CR already exists for user: {cr_name}")
                continue
            
            # Create CR
            user_cr = {
                'apiVersion': 'starlingx.io/v1',
                'kind': 'LocalLdapUser',
                'metadata': {
                    'name': cr_name,
                    'namespace': self.namespace,
                    'labels': {'imported': 'true'}
                },
                'spec': {
                    'uid': user_data['uid'],
                    'cn': user_data.get('cn'),
                    'sn': user_data.get('sn'),
                    'mail': user_data.get('mail', []),
                    'homeDirectory': user_data.get('homeDirectory'),
                    'loginShell': user_data.get('loginShell', '/bin/bash')
                }
            }
            
            await self._create_cr('localldapusers', user_cr)
            logger.info(f"Imported LDAP user as CR: {cr_name}")
    
    async def _import_groups(self):
        """Import existing LDAP groups as LocalLdapGroup CRs."""
        groups = await self.ldap_client.discover_groups()
        
        for group_data in groups:
            cr_name = group_data['cn']
            
            # Check if CR already exists
            if await self._cr_exists('localldapgroups', cr_name):
                logger.debug(f"CR already exists for group: {cr_name}")
                continue
            
            # Create CR
            group_cr = {
                'apiVersion': 'starlingx.io/v1',
                'kind': 'LocalLdapGroup',
                'metadata': {
                    'name': cr_name,
                    'namespace': self.namespace,
                    'labels': {'imported': 'true'}
                },
                'spec': {
                    'cn': group_data['cn'],
                    'description': group_data.get('description'),
                    'members': [
                        {'kind': 'LocalLdapUser', 'name': m}
                        for m in group_data.get('members', [])
                    ]
                }
            }
            
            await self._create_cr('localldapgroups', group_cr)
            logger.info(f"Imported LDAP group as CR: {cr_name}")
    
    async def _cr_exists(self, plural: str, name: str) -> bool:
        """Check if CR already exists."""
        try:
            self.k8s_client.get_namespaced_custom_object(
                group='starlingx.io',
                version='v1',
                namespace=self.namespace,
                plural=plural,
                name=name
            )
            return True
        except client.ApiException as e:
            if e.status == 404:
                return False
            raise
    
    async def _create_cr(self, plural: str, body: dict):
        """Create a custom resource."""
        self.k8s_client.create_namespaced_custom_object(
            group='starlingx.io',
            version='v1',
            namespace=self.namespace,
            plural=plural,
            body=body
        )