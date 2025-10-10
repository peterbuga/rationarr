from app.indexers.unit3d import Unit3d


class Yusceneapi(Unit3d):
    name = "YUSCENE"
    alias = "YUS"

    points_map = {
        500: {"value": "1", "desc": "2 GiB Upload"},
        1500: {"value": "2", "desc": "10 GiB Upload"},
        2000: {"value": "9", "desc": "1 Invite"},
        3000: {"value": "3", "desc": "25 GiB Upload"},
        9500: {"value": "4", "desc": "100 GiB Upload"},
        90000: {"value": "5", "desc": "1 TB Upload"},
        24000: {"value": "10", "desc": "Personal 24Hr Freeleech"},
        150000: {"value": "11", "desc": "Personal 1W Freeleech"},
    }
