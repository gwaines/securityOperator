"""LocalLdapUser model."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class LocalLdapUser:
    """Model for LocalLdapUser CRD."""
    
    name: str
    namespace: str
    uid: str
    cn: Optional[str] = None
    sn: Optional[str] = None
    given_name: Optional[str] = None
    display_name: Optional[str] = None
    mail: Optional[List[str]] = None
    user_password_secret: Optional[Dict[str, str]] = None
    pwd_reset: bool = True
    password_policy_ref: Optional[Dict[str, str]] = None
    home_directory: Optional[str] = None
    login_shell: str = "/bin/bash"
    
    @classmethod
    def from_spec(cls, spec: Dict[str, Any], name: str, namespace: str) -> 'LocalLdapUser':
        """Create LocalLdapUser from CRD spec."""
        return cls(
            name=name,
            namespace=namespace,
            uid=spec['uid'],
            cn=spec.get('cn'),
            sn=spec.get('sn'),
            given_name=spec.get('givenName'),
            display_name=spec.get('displayName'),
            mail=spec.get('mail', []),
            user_password_secret=spec.get('userPasswordSecret'),
            pwd_reset=spec.get('pwdReset', True),
            password_policy_ref=spec.get('passwordPolicyRef'),
            home_directory=spec.get('homeDirectory', f"/home/{spec['uid']}"),
            login_shell=spec.get('loginShell', "/bin/bash")
        )