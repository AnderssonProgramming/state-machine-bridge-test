class RuleError(Exception):
    pass


class RuleNotFoundError(RuleError):
    def __init__(self, rule_id: str) -> None:
        self.rule_id = rule_id
        super().__init__(f"Rule '{rule_id}' not found.")


class UnknownActionError(RuleError):
    def __init__(self, action_type: str) -> None:
        self.action_type = action_type
        super().__init__(f"Unknown action type: '{action_type}'.")


class InvalidConditionError(RuleError):
    pass
