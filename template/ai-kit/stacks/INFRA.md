# Infrastructure (Terraform/Helm)

Confirm tool versions, state backend, environments/workspaces, and the apply/review workflow before editing.
- Format and validate before plan: terraform fmt -check, terraform validate, then plan against the intended workspace; apply only after review and an explicit request.
- Keep state remote, locked, and separated per environment; never commit state, .terraform/, or secrets. Supply values through variables/TF_VAR or a secrets manager, not literals in tracked .tf/.tfvars files.
- Pin provider and module versions; review upgrade diffs and state-migration risk; keep modules small and composable with explicit variables and outputs.
- Prefer data sources and remote state over duplicating values; document required inputs in descriptions or the module README.
- Charts: lint and render before installing (helm lint, helm template with representative values); pin chart and image versions, set resource requests/limits, and honor values.schema.json where present.
- Keep rendered Kubernetes manifests aligned with the container contract (non-root, probes, resource requests); wire secrets through existing secret mechanisms, never plain values.
- Review plans and diffs for destructive changes (replace/destroy); protect production with approvals and, where configured, policy checks in CI.

Sources: [Terraform CLI](https://developer.hashicorp.com/terraform/cli), [Terraform language](https://developer.hashicorp.com/terraform/language), [Helm documentation](https://helm.sh/docs/).
