# StarlingX Security Operator Documentation

## Overview

The StarlingX Security Operator provides a declarative interface for managing LDAP users, groups, password policies, and Linux role bindings in a Kubernetes environment.

## Architecture

The operator is built using the KOPF framework and manages four main Custom Resource Definitions (CRDs):

- **LocalLdapUser**: Manages LDAP user accounts
- **LocalLdapGroup**: Manages LDAP groups and memberships
- **LocalLdapPasswordPolicy**: Manages password policies
- **LinuxRoleBinding**: Manages Linux group bindings for authorization

## Installation

### Prerequisites

- Kubernetes cluster (v1.20+)
- OpenLDAP/slapd deployment
- Helm 3.x

### Using Helm

```bash
helm install security-operator helm-chart/
```

### Manual Installation

1. Apply CRDs:
```bash
kubectl apply -f crds/
```

2. Deploy the operator:
```bash
kubectl apply -f deploy/
```

## Configuration

The operator can be configured through Helm values or environment variables:

- `LDAP_URI`: LDAP server URI (default: ldap://localhost:389)
- `LDAP_BIND_DN`: Bind DN for LDAP operations
- `LDAP_BIND_PASSWORD`: Bind password
- `LDAP_BASE_DN`: Base DN for LDAP operations

## Usage Examples

See the `examples/` directory for sample CRD manifests.

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for development setup and guidelines.

## API Reference

See [API.md](API.md) for detailed API documentation.