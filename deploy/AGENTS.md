# deploy/ — Agent Guide

This directory contains Kubernetes deployment manifests and infrastructure configuration.

## Structure

| Path             | Purpose                                       |
| ---------------- | --------------------------------------------- |
| `k8/`            | Kubernetes manifests, services, kustomization |
| `k8/services/`   | Per-service deployment configs                |
| `k8/monitoring/` | Monitoring and observability config           |
| `k8/misc/`       | Miscellaneous k8s resources                   |
| `package.json`   | Dependencies for deployment scripts           |

## Constraints

- **Do not modify deployment manifests** without explicit approval. These directly affect production infrastructure.
- **Do not change `kustomization.yaml`** — it controls which resources are applied.
- **Do not modify service resource limits** (CPU, memory) without benchmarking.
- Changes here are high-risk and should always go through human review.

## When you might need to look here

- Understanding how the game server is deployed (service topology, environment variables)
- Debugging deployment-related issues referenced in GitHub issues
- Reading (not modifying) config to understand infrastructure assumptions

## Validation

There is no local validation for k8s manifests beyond syntax checking. If you must edit here, ensure:

1. YAML is valid
2. The change is reviewed by someone familiar with the deployment environment
3. The PR is clearly labeled as infrastructure-affecting
