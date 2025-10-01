from app.schemas.common import EnhancedStrEnum, ScraperFields


class MyanonamouseScraperFields(EnhancedStrEnum):
    user = ScraperFields.user.value
    class_ = ScraperFields.user_class.value
    uploaded = ScraperFields.upload.value
    real_uploaded = ScraperFields.real_upload.value
    downloaded = ScraperFields.download.value
    real_downloaded = ScraperFields.real_download.value
    share_ratio = ScraperFields.ratio.value
    real_share_ratio = ScraperFields.real_ratio.value
    invites = ScraperFields.invites.value
    total_donated = ScraperFields.total_donate.value
    points = ScraperFields.points.value
    join_date = ScraperFields.join_date.value
    last_seen = ScraperFields.last_access.value
    torrent_comments = ScraperFields.comments.value
    forum_posts = ScraperFields.posts.value
    connectable = ScraperFields.connectable.value

    # address -
    # dynamic_seedbox -
    # seedbox -
    # agent -
    # invited_by -
    # requests -
    # fl_wedges -
    # staff_tickets -
    # points_earning - Last update was 2025-...
