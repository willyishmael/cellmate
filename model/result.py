from dataclasses import dataclass
from typing import List

@dataclass
class Result:
    success: bool
    data: List[dict]
    message: str = ""