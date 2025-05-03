# models/troop_manager.py
from typing import Dict, List
from constants import TROOP_TYPES, MAX_PERCENTAGE
from models.troop_count import TroopCount
from models.buffs import BuffConfiguration
import math

class TroopManager:
    def __init__(self, max_march_size: int, buffs: BuffConfiguration):
        self.max_march_size = max_march_size
        self.buffs = buffs
        self.effective_march_size = self.buffs.calculate_total_buff(max_march_size)

    def generate_marches(self, num_marches, troops: TroopCount, ratios: list[dict[str, float]]):
        total = troops.to_dict()
        marches = []

        for i in range(num_marches):
            r = ratios[i]
            if round(r['infantry'] + r['lancer'] + r['marksman'], 2) != 100.0:
                raise ValueError(f"March {i + 1} ratios must total 100%.")

            march = {'infantry': 0, 'lancer': 0, 'marksman': 0}

            # 1st pass: assign based on ceiling of ratio
            requested = {
                troop_type: math.ceil((r[troop_type] / 100) * self.effective_march_size)
                for troop_type in TROOP_TYPES
            }

            # Initial assignment with availability check
            for troop_type in TROOP_TYPES:
                march[troop_type] = min(requested[troop_type], total[troop_type])
                total[troop_type] -= march[troop_type]

            march_total = sum(march.values())

            # If we overfilled, trim lowest-priority troop types first
            if march_total > self.effective_march_size:
                overflow = march_total - self.effective_march_size
                # Priority: lowest ratio → highest ratio
                priority = sorted(TROOP_TYPES, key=lambda t: r[t])
                for troop_type in priority:
                    if overflow == 0:
                        break
                    reducible = min(march[troop_type], overflow)
                    march[troop_type] -= reducible
                    overflow -= reducible
                    march_total -= reducible

            # If we underfilled (rounding loss or exhausted types), backfill by priority
            elif march_total < self.effective_march_size:
                shortfall = self.effective_march_size - march_total
                # Priority: highest ratio → lowest
                priority = sorted(TROOP_TYPES, key=lambda t: -r[t])
                for troop_type in priority:
                    if shortfall == 0:
                        break
                    extra = min(shortfall, total[troop_type])
                    march[troop_type] += extra
                    total[troop_type] -= extra
                    shortfall -= extra
                    march_total += extra

            march['total'] = march_total
            marches.append(march)

        return marches

    def _generate_single_march(self, march_size: int, available_troops: Dict[str, int], ratio: Dict[str, float]) -> Dict[str, int]:
        if round(sum(ratio.values()), 2) != MAX_PERCENTAGE:
            raise ValueError("March ratios must total 100%.")

        march = {troop_type: 0 for troop_type in TROOP_TYPES}
        march['total'] = 0

        for troop_type in TROOP_TYPES:
            troops_count = int((ratio[troop_type] / 100) * march_size)
            march[troop_type] = min(troops_count, available_troops[troop_type])
            march['total'] += march[troop_type]

        return march

    def optimize_ratio(self, num_marches, troops: TroopCount, ratio_type: str) -> dict[str, float]:
        total_needed = num_marches * self.effective_march_size
        available = troops.to_dict()

        base_ratios = {
            "Bear": {"infantry": 10, "lancer": 30, "marksman": 60},
            "Infantry Focused": {"infantry": 60, "lancer": 30, "marksman": 10},
            "Balanced": {"infantry": 33.33, "lancer": 33.33, "marksman": 33.34},
            "Lancer Charge": {"infantry": 5, "lancer": 85, "marksman": 10},
            "Marksman Rush": {"infantry": 5, "lancer": 15, "marksman": 80},
            "Infantry Wall": {"infantry": 80, "lancer": 10, "marksman": 10}
        }.get(ratio_type, {"infantry": 33.33, "lancer": 33.33, "marksman": 33.34})

        # Calculate ideal troop count using ceil to avoid rounding down
        ideal = {
            t: math.ceil(base_ratios[t] / 100 * total_needed)
            for t in TROOP_TYPES
        }

        assigned = {t: 0 for t in TROOP_TYPES}
        remaining = total_needed

        # Distribute based on preferred priority
        priority = sorted(base_ratios.keys(), key=lambda t: -base_ratios[t])

        for t in priority:
            give = min(ideal[t], available[t], remaining)
            assigned[t] = give
            available[t] -= give
            remaining -= give
            if remaining == 0:
                break

        # Redistribute shortfall based on priority again
        if remaining > 0:
            for t in priority:
                if available[t] > 0:
                    extra = min(available[t], remaining)
                    assigned[t] += extra
                    available[t] -= extra
                    remaining -= extra
                if remaining == 0:
                    break

        total_assigned = sum(assigned.values())
        if total_assigned == 0:
            return {t: 0 for t in TROOP_TYPES}

        # Step 1: Calculate raw integer percentages
        raw_percentages = {
            t: int((assigned[t] / total_assigned) * 100)
            for t in TROOP_TYPES
        }

        # Step 2: Distribute remainder to closest troop type
        current_sum = sum(raw_percentages.values())
        remainder = 100 - current_sum

        # Find troop type with largest remainder part and add the leftover(s) to it
        if remainder > 0:
            # Calculate decimal remainders to determine where to add the extra
            remainders = {
                t: ((assigned[t] / total_assigned) * 100) - raw_percentages[t]
                for t in TROOP_TYPES
            }
            # Sort by largest remainder
            sorted_remainders = sorted(remainders.items(), key=lambda x: -x[1])
            for i in range(remainder):
                raw_percentages[sorted_remainders[i % len(TROOP_TYPES)][0]] += 1

        return raw_percentages