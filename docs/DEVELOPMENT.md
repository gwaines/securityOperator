# Development Guide

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd security-operator
```

2. Install development dependencies:
```bash
make install-dev
```

3. Run tests:
```bash
make test
```

## Project Structure

```
security-operator/
├── src/security_operator/          # Main package
│   ├── handlers/                   # KOPF event handlers
│   ├── models/                     # Data models
│   └── utils/                      # Utility modules
├── tests/                          # Test suite
│   ├── unit/                       # Unit tests
│   └── integration/                # Integration tests
├── crds/                           # Custom Resource Definitions
├── helm-chart/                     # Helm chart
└── docs/                           # Documentation
```

## Testing

- Unit tests: `make test-unit`
- Integration tests: `make test-integration`
- All tests: `make test`

## Code Quality

- Linting: `make lint`
- Formatting: `make format`

## Building

- Build package: `make build`
- Build Docker image: `make docker-build`

## Deployment

- Apply CRDs: `make apply-crds`
- Install with Helm: `make helm-install`