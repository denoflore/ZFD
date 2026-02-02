"""
Operator detection for ZFD pipeline.
Detects word-initial grammatical operators.
"""

import json
from typing import Tuple, Optional
from pathlib import Path


class OperatorDetector:
    def __init__(self, operators_file: str):
        with open(operators_file) as f:
            data = json.load(f)
        self.operators = {op['eva']: op for op in data['operators']}
        self.detection_order = data['detection_order']

    def detect(self, eva_token: str) -> Tuple[Optional[dict], str]:
        """
        Detect operator at start of token.

        Args:
            eva_token: EVA token string

        Returns:
            Tuple of (operator_dict or None, remaining_token)
        """
        for op_key in self.detection_order:
            if eva_token.startswith(op_key):
                remaining = eva_token[len(op_key):]
                return self.operators[op_key], remaining
        return None, eva_token

    def apply_to_token(self, token) -> str:
        """
        Apply operator detection to Token object.

        Returns:
            The remaining token after operator removal
        """
        op, remaining = self.detect(token.eva)
        if op:
            token.operator = op['croatian']
            token.operator_type = op['type']
            token.rewrites.append(f"operator: {op['eva']}→{op['croatian']}")
            token.confidence += 0.25
            token.notes.append(f"Operator {op['gloss']} ({op['status']})")
        return remaining
