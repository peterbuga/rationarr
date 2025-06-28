from app.schemas.common import EnhancedStrEnum, ScraperFields


class Unit3dScraperFields(EnhancedStrEnum):
    # username = "user"
    group = ScraperFields.user_class.value
    uploaded = ScraperFields.upload.value
    downloaded = ScraperFields.download.value
    ratio = ScraperFields.ratio.value
    buffer = ScraperFields.buffer.value
    seeding = ScraperFields.seed.value
    leeching = ScraperFields.leech.value
    seedbonus = ScraperFields.points.value
    hit_and_runs = ScraperFields.hnr.value
