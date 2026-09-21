# Persistence

## Repository and Unit of Work

One repository per aggregate root. The Unit of Work owns the transaction and spans every repository touched by a single use case, so an aggregate is never half-written.

The invariant is per transaction, not per use case. A use case that makes an external call it cannot roll back uses two: commit the intent, make the call with no transaction open, then commit the outcome. Never hold a transaction across network I/O — a slow provider will exhaust the connection pool, turning their bad afternoon into your outage. The durable intermediate row is only worth writing if something reads it, so this pattern ships with a reconciliation job that finds rows still pending past a threshold and settles them against the external system.

Repository interfaces live in `core/interfaces/`; SQLAlchemy implementations live in `infrastructure/database/`.

## Keeping the domain ORM-free

`core/` must not import SQLAlchemy. Entities are plain classes or dataclasses, not declarative models. `infrastructure/database/` holds the ORM models and mappers that translate between them.

The cost is a mapping layer. The benefit is that domain tests need no database and a storage change does not touch `core/`.

## Exception translation

Catch `sqlalchemy.exc.*` in the adapter and re-raise as a domain exception from `core/exceptions.py`, choosing the right base: a constraint violation such as `IntegrityError` is the caller's fault and becomes a `DomainError`, while `OperationalError`, `DisconnectionError`, and timeouts become a `TransientError` because the request was valid and may succeed on retry. Translating both into the same category is how an outage gets reported as a bad request.

```python
try:
    self._session.add(model)
    await self._session.flush()
except IntegrityError as err:
    raise DuplicateThingError(thing.thing_id) from err
```

A caller in `application/` should never need to import SQLAlchemy to handle an error.

## Migrations

Alembic, one migration per schema change, reviewed like code.

Deploy in backward-compatible steps so the old and new application versions can both run against the intermediate schema:

1. Add the new column as nullable, or add the new table.
2. Deploy code that writes both old and new, and backfill.
3. Deploy code that reads the new.
4. Drop the old column in a later migration.

Never combine a destructive change with the deploy that stops using the old shape.
