"""LDAP client for managing OpenLDAP/slapd operations."""

import ldap
import logging
import os
from typing import Optional
from security_operator.models.ldap_user import LocalLdapUser
from security_operator.models.ldap_group import LocalLdapGroup
from security_operator.models.password_policy import LocalLdapPasswordPolicy

logger = logging.getLogger(__name__)


class LdapClient:
    """Client for LDAP operations."""
    
    def __init__(self, ldap_uri: str = None, 
                 bind_dn: str = None,
                 bind_password: str = None):
        """Initialize LDAP client."""
        self.ldap_uri = ldap_uri or os.getenv('LDAP_URI', 'ldap://localhost:389')
        self.bind_dn = bind_dn or os.getenv('LDAP_BIND_DN', 'cn=admin,dc=example,dc=com')
        self.bind_password = bind_password or os.getenv('LDAP_BIND_PASSWORD', 'admin')
        self.base_dn = os.getenv('LDAP_BASE_DN', 'dc=example,dc=com')
        self.users_ou = f"ou=users,{self.base_dn}"
        self.groups_ou = f"ou=groups,{self.base_dn}"
        
    def _get_connection(self):
        """Get LDAP connection."""
        conn = ldap.initialize(self.ldap_uri)
        conn.simple_bind_s(self.bind_dn, self.bind_password)
        return conn
    
    async def create_user(self, user: LocalLdapUser) -> int:
        """Create LDAP user."""
        logger.info(f"Creating LDAP user: {user.uid}")
        
        # Generate UID number (simplified - should use proper allocation)
        uid_number = hash(user.uid) % 50000 + 10000
        
        user_dn = f"uid={user.uid},{self.users_ou}"
        attrs = {
            'objectClass': [b'inetOrgPerson', b'posixAccount'],
            'uid': [user.uid.encode()],
            'cn': [user.cn.encode() if user.cn else user.uid.encode()],
            'sn': [user.sn.encode() if user.sn else user.uid.encode()],
            'uidNumber': [str(uid_number).encode()],
            'gidNumber': [b'100'],
            'homeDirectory': [user.home_directory.encode()],
            'loginShell': [user.login_shell.encode()],
        }
        
        if user.mail:
            attrs['mail'] = [email.encode() for email in user.mail]
        
        conn = self._get_connection()
        try:
            conn.add_s(user_dn, list(attrs.items()))
            logger.info(f"Successfully created LDAP user: {user.uid}")
            return uid_number
        finally:
            conn.unbind_s()
    
    async def update_user(self, user: LocalLdapUser):
        """Update LDAP user."""
        logger.info(f"Updating LDAP user: {user.uid}")
        # Implementation for user updates
        pass
    
    async def delete_user(self, uid: str):
        """Delete LDAP user."""
        logger.info(f"Deleting LDAP user: {uid}")
        user_dn = f"uid={uid},{self.users_ou}"
        
        conn = self._get_connection()
        try:
            conn.delete_s(user_dn)
            logger.info(f"Successfully deleted LDAP user: {uid}")
        finally:
            conn.unbind_s()
    
    async def create_group(self, group: LocalLdapGroup) -> int:
        """Create LDAP group."""
        logger.info(f"Creating LDAP group: {group.cn}")
        
        # Generate GID number (simplified)
        gid_number = hash(group.cn) % 50000 + 20000
        
        group_dn = f"cn={group.cn},{self.groups_ou}"
        attrs = {
            'objectClass': [b'groupOfNames', b'posixGroup'],
            'cn': [group.cn.encode()],
            'gidNumber': [str(gid_number).encode()],
            'member': [b''],  # Will be updated with actual members
        }
        
        if group.description:
            attrs['description'] = [group.description.encode()]
        
        conn = self._get_connection()
        try:
            conn.add_s(group_dn, list(attrs.items()))
            logger.info(f"Successfully created LDAP group: {group.cn}")
            return gid_number
        finally:
            conn.unbind_s()
    
    async def update_group(self, group: LocalLdapGroup):
        """Update LDAP group."""
        logger.info(f"Updating LDAP group: {group.cn}")
        # Implementation for group updates
        pass
    
    async def delete_group(self, cn: str):
        """Delete LDAP group."""
        logger.info(f"Deleting LDAP group: {cn}")
        group_dn = f"cn={cn},{self.groups_ou}"
        
        conn = self._get_connection()
        try:
            conn.delete_s(group_dn)
            logger.info(f"Successfully deleted LDAP group: {cn}")
        finally:
            conn.unbind_s()
    
    async def create_password_policy(self, policy: LocalLdapPasswordPolicy):
        """Create password policy."""
        logger.info(f"Creating password policy: {policy.name}")
        # Implementation for password policy creation
        pass
    
    async def update_password_policy(self, policy: LocalLdapPasswordPolicy):
        """Update password policy."""
        logger.info(f"Updating password policy: {policy.name}")
        # Implementation for password policy updates
        pass
    
    async def delete_password_policy(self, name: str):
        """Delete password policy."""
        logger.info(f"Deleting password policy: {name}")
        # Implementation for password policy deletion
        pass
    
    async def discover_users(self) -> list:
        """Discover existing LDAP users."""
        conn = self._get_connection()
        try:
            results = conn.search_s(
                self.users_ou,
                ldap.SCOPE_ONELEVEL,
                '(objectClass=posixAccount)',
                ['uid', 'cn', 'sn', 'mail', 'homeDirectory', 'loginShell']
            )
            
            users = []
            for dn, attrs in results:
                user_data = {
                    'uid': attrs.get('uid', [b''])[0].decode(),
                    'cn': attrs.get('cn', [b''])[0].decode() or None,
                    'sn': attrs.get('sn', [b''])[0].decode() or None,
                    'homeDirectory': attrs.get('homeDirectory', [b''])[0].decode() or None,
                    'loginShell': attrs.get('loginShell', [b'/bin/bash'])[0].decode(),
                }
                if attrs.get('mail'):
                    user_data['mail'] = [email.decode() for email in attrs['mail']]
                users.append(user_data)
            
            return users
        finally:
            conn.unbind_s()
    
    async def discover_groups(self) -> list:
        """Discover existing LDAP groups."""
        conn = self._get_connection()
        try:
            results = conn.search_s(
                self.groups_ou,
                ldap.SCOPE_ONELEVEL,
                '(objectClass=posixGroup)',
                ['cn', 'description']
            )
            
            groups = []
            for dn, attrs in results:
                group_data = {
                    'cn': attrs.get('cn', [b''])[0].decode(),
                    'description': attrs.get('description', [b''])[0].decode() or None,
                }
                groups.append(group_data)
            
            return groups
        finally:
            conn.unbind_s()