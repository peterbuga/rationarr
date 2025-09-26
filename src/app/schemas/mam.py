from app.schemas.common import EnhancedStrEnum, ScraperFields


class MamScraperFields(EnhancedStrEnum):
    # username = "user"
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
