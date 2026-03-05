"""Unit tests for data models."""

import pytest
from security_operator.models.ldap_user import LocalLdapUser
from security_operator.models.ldap_group import LocalLdapGroup
from security_operator.models.password_policy import LocalLdapPasswordPolicy
from security_operator.models.linux_role_binding import LinuxRoleBinding


def test_local_ldap_user_from_spec():
    """Test LocalLdapUser creation from spec."""
    spec = {
        'uid': 'testuser',
        'cn': 'Test User',
        'sn': 'User',
        'mail': ['test@example.com'],
        'pwdReset': False
    }
    
    user = LocalLdapUser.from_spec(spec, 'testuser', 'default')
    
    assert user.name == 'testuser'
    assert user.namespace == 'default'
    assert user.uid == 'testuser'
    assert user.cn == 'Test User'
    assert user.sn == 'User'
    assert user.mail == ['test@example.com']
    assert user.pwd_reset is False
    assert user.home_directory == '/home/testuser'


def test_local_ldap_group_from_spec():
    """Test LocalLdapGroup creation from spec."""
    spec = {
        'cn': 'testgroup',
        'description': 'Test Group',
        'members': [
            {'kind': 'LocalLdapUser', 'name': 'user1'},
            {'kind': 'LocalLdapGroup', 'name': 'group1'}
        ]
    }
    
    group = LocalLdapGroup.from_spec(spec, 'testgroup', 'default')
    
    assert group.name == 'testgroup'
    assert group.namespace == 'default'
    assert group.cn == 'testgroup'
    assert group.description == 'Test Group'
    assert len(group.members) == 2
    assert group.members[0].kind == 'LocalLdapUser'
    assert group.members[0].name == 'user1'


def test_password_policy_from_spec():
    """Test LocalLdapPasswordPolicy creation from spec."""
    spec = {
        'pwdMinLength': 8,
        'pwdMaxAge': 3600,
        'pwdLockout': False
    }
    
    policy = LocalLdapPasswordPolicy.from_spec(spec, 'testpolicy', 'default')
    
    assert policy.name == 'testpolicy'
    assert policy.namespace == 'default'
    assert policy.pwd_min_length == 8
    assert policy.pwd_max_age == 3600
    assert policy.pwd_lockout is False


def test_linux_role_binding_from_spec():
    """Test LinuxRoleBinding creation from spec."""
    spec = {
        'description': 'Test binding',
        'subjects': {
            'users': ['user1', 'user2'],
            'groups': ['group1']
        },
        'role': {
            'linuxGroups': ['sudo', 'docker']
        }
    }
    
    binding = LinuxRoleBinding.from_spec(spec, 'testbinding', 'default')
    
    assert binding.name == 'testbinding'
    assert binding.namespace == 'default'
    assert binding.description == 'Test binding'
    assert binding.subjects.users == ['user1', 'user2']
    assert binding.subjects.groups == ['group1']
    assert binding.role.linux_groups == ['sudo', 'docker']