#!/usr/bin/env python3
"""
StarlingX Security Operator

Main entry point for the Kubernetes operator that manages LDAP users,
groups, password policies, and Linux role bindings.
"""

import asyncio
import logging
import kopf
from security_operator.handlers import ldap_user, ldap_group, password_policy, linux_role_binding
from security_operator.utils.discovery import LdapDiscoveryService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@kopf.on.startup()
async def startup_handler(**kwargs):
    """Handle operator startup - discover existing LDAP entries."""
    logger.info("Operator starting up - beginning LDAP discovery")
    discovery = LdapDiscoveryService()
    await discovery.discover_and_import()


def main():
    """Main entry point for the operator."""
    logger.info("Starting StarlingX Security Operator")
    kopf.run()


if __name__ == "__main__":
    main()