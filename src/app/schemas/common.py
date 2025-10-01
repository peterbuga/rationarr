from enum import StrEnum


class EnhancedStrEnum(StrEnum):
    @classmethod
    def get_values(cls) -> list:
        return [member.value for member in cls]

    @classmethod
    def get_keys(cls) -> list:
        return list(cls.__members__)


# map scrapped fields to a fixed internal list of attributes
# format: `scrapped-field` = "`internal-field`"
class ScraperFields(EnhancedStrEnum):
    user = "user"
    email = "email"
    user_class = "user_class"
    upload = "upload"
    download = "download"
    real_upload = "real_upload"
    real_download = "real_download"
    ratio = "ratio"
    real_ratio = "real_ratio"
    buffer = "buffer"
    seed = "seed"
    leech = "leech"
    points = "points"
    hnr = "hnr"
    invites = "invites"
    total_donate = "total_donate"
    join_date = "join_date"
    balance = "balance"
    freeleech = "freeleech"
    last_access = "last_access"
    connectable = "connectable"
    comments = "comments"  # torrent comments
    posts = "posts"  # forum posts
