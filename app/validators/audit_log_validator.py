import json


def parse_json_field(v: str | None):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return None
        return v
    
def cap_page_size(v: int):
        return min(v, 200)