# Modular monolith vs distributed services

Default to a modular monolith. Extract a service only when there is a concrete driver: independent scaling, separate team ownership, or an independent deploy cadence. "It feels cleaner" is not a driver.

A well-bounded module in a monolith can be extracted later; a premature service cannot be merged back cheaply.

## If extracting a service

Define before writing code:

- The boundary and which data it exclusively owns. Two services must never write the same table.
- The API contract as OpenAPI or a `.proto` file, versioned and published.
- The compatibility policy: additive changes only within a major version; consumers upgrade independently.

## Communication

- **Synchronous** (FastAPI, gRPC) for request/response where the caller needs the result to continue. Set explicit timeouts, and decide the failure behavior of every call.
- **Asynchronous** (Kafka, RabbitMQ, SNS/SQS) for events where the caller does not need a result.

Async messaging is only correct if handlers are idempotent, because at-least-once delivery means every message will eventually arrive twice. Give every message a stable ID and make handlers safe to replay. Configure retries with backoff and a dead-letter queue; a message that fails forever must land somewhere a human can inspect it.
