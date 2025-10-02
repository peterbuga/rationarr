from app.indexers.unit3d import Unit3d


class Darkpeers(Unit3d):
    name = "Darkpeers"
    alias = "DP"

    points_map = {
        2500: {"value": "1", "desc": "50 GiB Upload"},
        5000: {"value": "2", "desc": "100 GiB Upload"},
        10000: {"value": "3", "desc": "250 GiB Upload"},
        20000: {"value": "4", "desc": "500 GiB Upload"},
        35000: {"value": "11", "desc": "1 TiB Upload"},
        165000: {"value": "13", "desc": "5 TiB Upload"},
        320000: {"value": "12", "desc": "10 TiB Upload"},
    }
