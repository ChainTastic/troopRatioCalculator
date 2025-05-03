# models/troop_count.py
from dataclasses import dataclass
from typing import Dict

@dataclass
class TroopCount:
    infantry: int
    lancer: int
    marksman: int

    def to_dict(self) -> Dict[str, int]:
        return {
            'infantry': self.infantry,
            'lancer': self.lancer,
            'marksman': self.marksman
        }
