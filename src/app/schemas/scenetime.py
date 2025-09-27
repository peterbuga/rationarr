from app.schemas.common import EnhancedStrEnum, ScraperFields


class ScenetimeScraperFields(EnhancedStrEnum):
    user = ScraperFields.user.value
    e_mail = ScraperFields.email.value
    class_ = ScraperFields.user_class.value
    uploaded = ScraperFields.upload.value
    downloaded = ScraperFields.download.value
    share_ratio = ScraperFields.ratio.value
    invites = ScraperFields.invites.value
    balance = ScraperFields.balance.value
    bonus_points = ScraperFields.points.value
    hit_runs = ScraperFields.hnr.value
    seeding = ScraperFields.seed.value
    leeching = ScraperFields.leech.value
    torrent_comments = ScraperFields.comments.value
    forum_posts = ScraperFields.posts.value
    join_date = ScraperFields.join_date.value
