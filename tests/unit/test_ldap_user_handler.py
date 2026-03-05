"""Unit tests for LDAP user handler."""

import pytest
from unittest.mock import AsyncMock, patch
from security_operator.handlers.ldap_user import create_ldap_user, update_ldap_user, delete_ldap_user


@pytest.mark.asyncio
async def test_create_ldap_user():
    """Test LDAP user creation."""
    spec = {
        'uid': 'testuser',
        'cn': 'Test User',
        'sn': 'User',
        'mail': ['test@example.com']
    }
    
    with patch('security_operator.handlers.ldap_user.LdapClient') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance
        mock_instance.create_user.return_value = 10001
        
        result = await create_ldap_user(spec, 'testuser', 'default')
        
        assert result['uidNumber'] == 10001
        assert result['gidNumber'] == 100
        assert result['temporaryLockOut'] is False


@pytest.mark.asyncio
async def test_update_ldap_user():
    """Test LDAP user update."""
    spec = {
        'uid': 'testuser',
        'cn': 'Updated User'
    }
    
    with patch('security_operator.handlers.ldap_user.LdapClient') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance
        
        result = await update_ldap_user(spec, 'testuser', 'default')
        
        assert result['updated'] is True


@pytest.mark.asyncio
async def test_delete_ldap_user():
    """Test LDAP user deletion."""
    spec = {'uid': 'testuser'}
    
    with patch('security_operator.handlers.ldap_user.LdapClient') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance
        
        # Should not raise exception
        await delete_ldap_user(spec, 'testuser', 'default')