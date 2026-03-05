"""LocalLdapGroup model."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class GroupMember:
    """Model for group member reference."""
    kind: str
    name: str


@dataclass
class LocalLdapGroup:
    """Model for LocalLdapGroup CRD."""
    
    name: str
    namespace: str
    cn: str
    description: Optional[str] = None
    members: Optional[List[GroupMember]] = None
    
    @classmethod
    def from_spec(cls, spec: Dict[str, Any], name: str, namespace: str) -> 'LocalLdapGroup':
        """Create LocalLdapGroup from CRD spec."""
        members = []
        if spec.get('members'):
            for member in spec['members']:
                members.append(GroupMember(
                    kind=member['kind'],
                    name=member['name']
                ))
        
        return cls(
            name=name,
            namespace=namespace,
            cn=spec['cn'],
            description=spec.get('description'),
            members=members if members else None
        )