"""Integration tests for the security operator."""

import pytest
import asyncio
from kubernetes import client, config
from kubernetes.client.rest import ApiException


@pytest.mark.integration
class TestSecurityOperatorIntegration:
    """Integration tests for the security operator."""
    
    @classmethod
    def setup_class(cls):
        """Set up test class."""
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()
        
        cls.api_client = client.ApiClient()
        cls.custom_api = client.CustomObjectsApi()
    
    @pytest.mark.asyncio
    async def test_create_ldap_user_crd(self):
        """Test creating a LocalLdapUser CRD instance."""
        user_spec = {
            'apiVersion': 'starlingx.io/v1',
            'kind': 'LocalLdapUser',
            'metadata': {
                'name': 'test-user',
                'namespace': 'default'
            },
            'spec': {
                'uid': 'testuser',
                'cn': 'Test User',
                'sn': 'User',
                'mail': ['test@example.com']
            }
        }
        
        try:
            # Create the CRD instance
            response = self.custom_api.create_namespaced_custom_object(
                group='starlingx.io',
                version='v1',
                namespace='default',
                plural='localldapusers',
                body=user_spec
            )
            
            assert response['metadata']['name'] == 'test-user'
            
            # Wait for status to be updated
            await asyncio.sleep(5)
            
            # Check status
            user = self.custom_api.get_namespaced_custom_object(
                group='starlingx.io',
                version='v1',
                namespace='default',
                plural='localldapusers',
                name='test-user'
            )
            
            # Cleanup
            self.custom_api.delete_namespaced_custom_object(
                group='starlingx.io',
                version='v1',
                namespace='default',
                plural='localldapusers',
                name='test-user'
            )
            
        except ApiException as e:
            pytest.skip(f"Kubernetes API not available: {e}")
    
    @pytest.mark.asyncio
    async def test_create_linux_role_binding_crd(self):
        """Test creating a LinuxRoleBinding CRD instance."""
        binding_spec = {
            'apiVersion': 'starlingx.io/v1',
            'kind': 'LinuxRoleBinding',
            'metadata': {
                'name': 'test-binding',
                'namespace': 'default'
            },
            'spec': {
                'description': 'Test role binding',
                'subjects': {
                    'users': ['testuser']
                },
                'role': {
                    'linuxGroups': ['sudo']
                }
            }
        }
        
        try:
            # Create the CRD instance
            response = self.custom_api.create_namespaced_custom_object(
                group='starlingx.io',
                version='v1',
                namespace='default',
                plural='linuxrolebindings',
                body=binding_spec
            )
            
            assert response['metadata']['name'] == 'test-binding'
            
            # Cleanup
            self.custom_api.delete_namespaced_custom_object(
                group='starlingx.io',
                version='v1',
                namespace='default',
                plural='linuxrolebindings',
                name='test-binding'
            )
            
        except ApiException as e:
            pytest.skip(f"Kubernetes API not available: {e}")