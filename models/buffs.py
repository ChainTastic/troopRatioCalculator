# models/buffs.py
from dataclasses import dataclass

@dataclass
class BuffConfiguration:
    pet_buff: int
    city_buff: int
    minister_buff: int

    def calculate_total_buff(self, base_march_size: int) -> int:
        city_buff_value = int(base_march_size * self.city_buff / 100)
        return base_march_size + self.pet_buff + city_buff_value + self.minister_buff
