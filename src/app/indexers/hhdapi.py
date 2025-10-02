from app.indexers.unit3d import Unit3d


class Hhdapi(Unit3d):
    name = "HomieHelpDesk"
    alias = "HHD"

    points_map = {
        2500: {"value": "1", "desc": "2 GiB Upload"},
        5500: {"value": "2", "desc": "5 GiB Upload"},
        10000: {"value": "3", "desc": "10 GiB Upload"},
        25000: {"value": "4", "desc": "25 GiB Upload"},
        90000: {"value": "9", "desc": "100 GiB Upload"},
    }
