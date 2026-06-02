from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.order import Order
from src.domain.rules.execution_log import RuleExecutionLog
from src.domain.rules.rule import Rule
from src.domain.states import OrderState
from src.handlers.dependencies import (
    get_rule_engine,
    get_rule_log_repository,
    get_rule_repository,
)
from src.models.rule_schemas import (
    CreateRuleRequest,
    DryRunRequest,
    DryRunResponse,
    ToggleEnabledRequest,
    UpdateRuleRequest,
)
from src.repositories.base import RuleLogRepository, RuleRepository
from src.services.rules.engine import RuleEngineService

router = APIRouter(prefix="/rules", tags=["rules"])


def _get_or_404(repo: RuleRepository, rule_id: str) -> Rule:
    rule = repo.get_by_id(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found.")
    return rule


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


@router.post("", status_code=status.HTTP_201_CREATED, response_model_by_alias=True)
def create_rule(
    payload: CreateRuleRequest,
    repo: Annotated[RuleRepository, Depends(get_rule_repository)],
) -> Rule:
    rule = Rule(**payload.model_dump(by_alias=False))
    repo.save(rule)
    return rule


@router.get("", response_model_by_alias=True)
def list_rules(
    repo: Annotated[RuleRepository, Depends(get_rule_repository)],
    trigger: str | None = None,
    enabled: bool | None = None,
) -> list[Rule]:
    rules = repo.list_all()
    if trigger is not None:
        rules = [r for r in rules if r.trigger == trigger]
    if enabled is not None:
        rules = [r for r in rules if r.enabled == enabled]
    rules.sort(key=lambda r: r.priority)
    return rules


@router.get("/{rule_id}", response_model_by_alias=True)
def get_rule(
    rule_id: str,
    repo: Annotated[RuleRepository, Depends(get_rule_repository)],
) -> Rule:
    return _get_or_404(repo, rule_id)


@router.put("/{rule_id}", response_model_by_alias=True)
def update_rule(
    rule_id: str,
    payload: UpdateRuleRequest,
    repo: Annotated[RuleRepository, Depends(get_rule_repository)],
) -> Rule:
    rule = _get_or_404(repo, rule_id)

    # Get current and update data
    current_data = rule.model_dump(by_alias=False)
    update_data = payload.model_dump(exclude_unset=True, by_alias=False)

    # Merge them
    current_data.update(update_data)
    current_data["version"] = rule.version + 1
    current_data["updated_at"] = _utc_now()

    # Force a full re-validation of the entire structure
    # This should correctly parse the dict back into appropriate Node types
    updated = Rule(**current_data)
    repo.save(updated)
    return updated


@router.patch("/{rule_id}/enabled", response_model_by_alias=True)
def toggle_enabled(
    rule_id: str,
    payload: ToggleEnabledRequest,
    repo: Annotated[RuleRepository, Depends(get_rule_repository)],
) -> Rule:
    rule = _get_or_404(repo, rule_id)
    updated = rule.model_copy(
        update={
            "enabled": payload.enabled,
            "version": rule.version + 1,
            "updated_at": _utc_now(),
        }
    )
    repo.save(updated)
    return updated


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: str,
    repo: Annotated[RuleRepository, Depends(get_rule_repository)],
) -> None:
    if not repo.delete(rule_id):
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found.")


@router.post("/{rule_id}/dry-run", response_model_by_alias=True)
def dry_run(
    rule_id: str,
    payload: DryRunRequest,
    repo: Annotated[RuleRepository, Depends(get_rule_repository)],
    engine: Annotated[RuleEngineService, Depends(get_rule_engine)],
) -> DryRunResponse:
    rule = _get_or_404(repo, rule_id)
    sample_order = Order(
        product_ids=payload.product_ids,
        amount=payload.amount,
        attributes=payload.attributes,
        state=OrderState.PENDING,
    )
    matched, results = engine.dry_run(rule, sample_order)
    return DryRunResponse(matched=matched, actions=results)


@router.get("/_logs/by-order/{order_id}", response_model_by_alias=True)
def logs_for_order(
    order_id: str,
    log_repo: Annotated[RuleLogRepository, Depends(get_rule_log_repository)],
) -> list[RuleExecutionLog]:
    return log_repo.list_for_order(order_id)
