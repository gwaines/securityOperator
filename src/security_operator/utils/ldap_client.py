"""LDAP client for managing OpenLDAP/slapd operations."""

import ldap
import logging
import os
import base64
from typing import Optional
from kubernetes import client, config
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
        self.users_ou = os.getenv('LDAP_USERS_OU', f"ou=People,{self.base_dn}")
        self.groups_ou = os.getenv('LDAP_GROUPS_OU', f"ou=Groups,{self.base_dn}")
        
        # Initialize Kubernetes client for secret access
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()
        self.k8s_client = client.CoreV1Api()
        
    def _get_connection(self):
        """Get LDAP connection."""
        conn = ldap.initialize(self.ldap_uri)
        conn.simple_bind_s(self.bind_dn, self.bind_password)
        return conn
    
    async def create_user(self, user: LocalLdapUser) -> int:
        """Create LDAP user."""
        logger.info(f"Creating LDAP user: {user.uid}")
        
        # Find next available UID number
        uid_number = await self._get_next_available_uid()
        
        # Determine password and pwdReset behavior
        if user.user_password_secret:
            try:
                password = await self._get_password_from_secret(
                    user.user_password_secret['name'],
                    user.user_password_secret.get('key', 'password'),
                    user.namespace
                )
                pwd_reset = False  # Custom password, no reset required
                logger.info(f"Using custom password from secret for user: {user.uid}")
            except Exception as e:
                logger.warning(f"Failed to fetch password from secret for {user.uid}: {e}. Using username as password.")
                password = user.uid
                pwd_reset = True
        else:
            # No password specified - use username and force reset
            password = user.uid
            pwd_reset = True
        
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
            'userPassword': [password.encode()],
        }
        
        # Set pwdReset attribute for password policy
        if pwd_reset:
            attrs['pwdReset'] = [b'TRUE']
        else:
            attrs['pwdReset'] = [b'FALSE']
        
        # Add optional attributes
        if user.mail:
            attrs['mail'] = [email.encode() for email in user.mail]
        
        if user.given_name:
            attrs['givenName'] = [user.given_name.encode()]
        
        if user.display_name:
            attrs['displayName'] = [user.display_name.encode()]
        
        conn = self._get_connection()
        try:
            conn.add_s(user_dn, list(attrs.items()))
            logger.info(f"Successfully created LDAP user: {user.uid} with UID {uid_number} (password: {password}, pwdReset: {pwd_reset})")
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
        
        # Find next available GID number
        gid_number = await self._get_next_available_gid()
        
        group_dn = f"cn={group.cn},{self.groups_ou}"
        attrs = {
            'objectClass': [b'posixGroup'],
            'cn': [group.cn.encode()],
            'gidNumber': [str(gid_number).encode()],
        }
        
        if group.description:
            attrs['description'] = [group.description.encode()]
        
        conn = self._get_connection()
        try:
            conn.add_s(group_dn, list(attrs.items()))
            logger.info(f"Successfully created LDAP group: {group.cn} with GID {gid_number}")
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
                ['uid', 'cn', 'sn', 'mail', 'homeDirectory', 'loginShell', 'uidNumber', 'pwdReset']
            )
            
            users = []
            for dn, attrs in results:
                uid_num = attrs.get('uidNumber', [b''])[0].decode()
                pwd_reset = attrs.get('pwdReset', [b'FALSE'])[0].decode().upper() == 'TRUE'
                user_data = {
                    'uid': attrs.get('uid', [b''])[0].decode(),
                    'cn': attrs.get('cn', [b''])[0].decode() or None,
                    'sn': attrs.get('sn', [b''])[0].decode() or None,
                    'homeDirectory': attrs.get('homeDirectory', [b''])[0].decode() or None,
                    'loginShell': attrs.get('loginShell', [b'/bin/bash'])[0].decode(),
                    'uidNumber': int(uid_num) if uid_num else None,
                    'pwdReset': pwd_reset,
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
                ['cn', 'gidNumber', 'memberUid', 'description']
            )
            
            groups = []
            for dn, attrs in results:
                gid = attrs.get('gidNumber', [b''])[0].decode()
                # Explicit memberUid attributes
                members = [m.decode() for m in attrs.get('memberUid', [])]
                # Find users whose primary gidNumber matches this group
                if gid:
                    primary_members = conn.search_s(
                        self.users_ou,
                        ldap.SCOPE_ONELEVEL,
                        f'(&(objectClass=posixAccount)(gidNumber={gid}))',
                        ['uid']
                    )
                    for _, user_attrs in primary_members:
                        uid = user_attrs.get('uid', [b''])[0].decode()
                        if uid and uid not in members:
                            members.append(uid)
                
                group_data = {
                    'cn': attrs.get('cn', [b''])[0].decode(),
                    'description': attrs.get('description', [b''])[0].decode() or None,
                    'members': members,
                    'gidNumber': int(gid) if gid else None,
                }
                groups.append(group_data)
            
            return groups
        finally:
            conn.unbind_s()
    
    async def _get_next_available_gid(self, start_gid: int = 10000) -> int:
        """Find the next available GID number."""
        conn = self._get_connection()
        try:
            # Get all existing GID numbers
            results = conn.search_s(
                self.groups_ou,
                ldap.SCOPE_ONELEVEL,
                '(objectClass=posixGroup)',
                ['gidNumber']
            )
            
            existing_gids = set()
            for _, attrs in results:
                gid = attrs.get('gidNumber', [b''])[0].decode()
                if gid:
                    existing_gids.add(int(gid))
            
            # Find next available GID starting from start_gid
            gid = start_gid
            while gid in existing_gids:
                gid += 1
            
            return gid
        finally:
            conn.unbind_s()
    
    async def _get_next_available_uid(self, start_uid: int = 10000) -> int:
        """Find the next available UID number."""
        conn = self._get_connection()
        try:
            # Get all existing UID numbers
            results = conn.search_s(
                self.users_ou,
                ldap.SCOPE_ONELEVEL,
                '(objectClass=posixAccount)',
                ['uidNumber']
            )
            
            existing_uids = set()
            for _, attrs in results:
                uid = attrs.get('uidNumber', [b''])[0].decode()
                if uid:
                    existing_uids.add(int(uid))
            
            # Find next available UID starting from start_uid
            uid = start_uid
            while uid in existing_uids:
                uid += 1
            
            return uid
        finally:
            conn.unbind_s()
    
    async def _get_password_from_secret(self, secret_name: str, key: str, namespace: str) -> str:
        """Fetch password from Kubernetes Secret."""
        try:
            secret = self.k8s_client.read_namespaced_secret(secret_name, namespace)
            if key not in secret.data:
                raise ValueError(f"Key '{key}' not found in secret '{secret_name}'")
            
            # Decode base64 encoded secret data
            password_bytes = base64.b64decode(secret.data[key])
            return password_bytes.decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to read secret {secret_name}/{key}: {e}")