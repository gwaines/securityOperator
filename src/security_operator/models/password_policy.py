"""LocalLdapPasswordPolicy model."""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class LocalLdapPasswordPolicy:
    """Model for LocalLdapPasswordPolicy CRD."""
    
    name: str
    namespace: str
    pwd_min_length: int = 12
    pwd_max_age: int = 7776000  # 90 days
    pwd_in_history: int = 5
    pwd_lockout: bool = True
    pwd_max_failure: int = 3
    pwd_lockout_duration: int = 300  # 5 minutes
    pwd_check_quality: int = 2
    pwd_expire_warning: int = 604800  # 7 days
    pwd_grace_authn_limit: int = 2
    
    @classmethod
    def from_spec(cls, spec: Dict[str, Any], name: str, namespace: str) -> 'LocalLdapPasswordPolicy':
        """Create LocalLdapPasswordPolicy from CRD spec."""
        return cls(
            name=name,
            namespace=namespace,
            pwd_min_length=spec.get('pwdMinLength', 12),
            pwd_max_age=spec.get('pwdMaxAge', 7776000),
            pwd_in_history=spec.get('pwdInHistory', 5),
            pwd_lockout=spec.get('pwdLockout', True),
            pwd_max_failure=spec.get('pwdMaxFailure', 3),
            pwd_lockout_duration=spec.get('pwdLockoutDuration', 300),
            pwd_check_quality=spec.get('pwdCheckQuality', 2),
            pwd_expire_warning=spec.get('pwdExpireWarning', 604800),
            pwd_grace_authn_limit=spec.get('pwdGraceAuthnLimit', 2)
        )