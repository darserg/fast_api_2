from src.core.config import settings


def setup_observability(app) -> None:
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.ENVIRONMENT,
                traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
                integrations=[FastApiIntegration(), SqlalchemyIntegration()],
            )
        except ImportError:
            pass

    if settings.OTEL_ENABLED:
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

            FastAPIInstrumentor.instrument_app(app)
            SQLAlchemyInstrumentor().instrument(engine=app.state.database.engine.sync_engine)
        except ImportError:
            pass
