"""LinuxRoleBinding model."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class Subjects:
    """Model for role binding subjects."""
    users: Optional[List[str]] = None
    groups: Optional[List[str]] = None


@dataclass
class Role:
    """Model for role binding role."""
    linux_groups: List[str]


@dataclass
class LinuxRoleBinding:
    """Model for LinuxRoleBinding CRD."""
    
    name: str
    namespace: str
    description: Optional[str] = None
    subjects: Optional[Subjects] = None
    role: Optional[Role] = None
    
    @classmethod
    def from_spec(cls, spec: Dict[str, Any], name: str, namespace: str) -> 'LinuxRoleBinding':
        """Create LinuxRoleBinding from CRD spec."""
        subjects = None
        if spec.get('subjects'):
            subjects = Subjects(
                users=spec['subjects'].get('users'),
                groups=spec['subjects'].get('groups')
            )
        
        role = None
        if spec.get('role'):
            role = Role(
                linux_groups=spec['role'].get('linuxGroups', [])
            )
        
        return cls(
            name=name,
            namespace=namespace,
            description=spec.get('description'),
            subjects=subjects,
            role=role
        )