"""Centralized AWS Lambda Powertools instances (shared singletons)."""

from aws_lambda_powertools import Logger, Metrics, Tracer

from src.config import get_settings

_settings = get_settings()

logger: Logger = Logger(service=_settings.powertools_service_name)
tracer: Tracer = Tracer(service=_settings.powertools_service_name)
metrics: Metrics = Metrics(namespace="OrderStateMachine")