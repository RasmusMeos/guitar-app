from typing import Dict, List, Tuple, Any

def pythonic_to_json(payload: Dict[str, List[Tuple[int, int]]]) -> Dict[str, List[List[int]]]:
    converted = {k: [list(pair) for pair in v] for k, v in payload.items()}
    return converted

def json_to_pythonic(converted: Dict[str, List[List[int]]]) -> Dict[str, List[Tuple[int, int]]]:
    result: Dict[str, List[Tuple[int, int]]] = {}
    for k, v in converted.items():
        if not isinstance(k, str):
            raise ValueError("Akord pole sõne tüüpi!")
        if not isinstance(v, list):
            raise ValueError(f"{k} võtme väärtus peab olema list!")

        tuples: List[Tuple[int, int]] = []
        for pair in v:
            if (not isinstance(pair, list) or len(pair) != 2 or
            not all(isinstance(n, int) for n in pair)):
                raise ValueError("Iga list peab olema kaheliikmeline ja koosnema int-tüüpi väärtustest!")
            tuples.append((pair[0], pair[1]))
        result[k] = tuples
    return result

