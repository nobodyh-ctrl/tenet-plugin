# AWS reference

AWS is the initial cloud reference. Each service below is listed for a concrete use case. None is required for every project. Verify current features, regional availability and pricing before adopting a service.

## Standards

- **MUST** Use AWS Organizations with separate accounts per environment for anything beyond experiments. Use IAM Identity Center for human access, and never root access keys.
- **MUST** Enable CloudTrail (organization trail) in every account. Store logs in a dedicated, protected S3 bucket.
- **MUST** Set AWS Budgets alerts for every account.
- **MUST** Keep S3 Block Public Access enabled at the account level unless a reviewed exception exists.
- **SHOULD** Authenticate CI with GitHub Actions OIDC to IAM roles scoped per repository and environment.
- **SHOULD** Store secrets in Secrets Manager (rotation) or SSM Parameter Store SecureString (simple config), encrypted with KMS.
- **SHOULD** Enable GuardDuty and Security Hub in every account.
- **SHOULD** Use CloudWatch for logs, metrics and alarms. Set log retention explicitly, because the default is never expire.

## Services by use case

| Use case | Default | Consider instead when |
|---|---|---|
| HTTP API, spiky or low traffic | API Gateway + Lambda | Sustained traffic or long requests → ECS Fargate behind an ALB |
| Containerized service | ECS Fargate | Many services and platform needs → EKS |
| Static site or SPA | S3 + CloudFront (OAC) | |
| Relational data | RDS (PostgreSQL/MySQL) or Aurora Serverless v2 | |
| Key-value at scale | DynamoDB | |
| Events and scheduling | EventBridge | Ordered queues → SQS FIFO |
| Async work queue | SQS | |
| Network isolation | VPC with private subnets, VPC endpoints | |
| Encryption keys | KMS | |

## Cost notes

- Billing traps: NAT Gateways, idle load balancers, unattached EBS volumes and over-provisioned RDS. Check them first.
- Labs: use the Free Tier where it applies, set a budget alert before starting, and tear everything down in the same session.
