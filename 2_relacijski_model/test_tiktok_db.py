import unittest
import pandas as pd
import sqlalchemy
from sqlalchemy import text
from pandas.testing import assert_frame_equal

class TestTikTokDatabase(unittest.TestCase):
    def setUp(self):
        self.engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/zavrsni_rad')
        self.connection = self.engine.connect()

        self.df = pd.read_csv("social_media_trends_PROCESSED.csv")

        query = """
SELECT
    p.name              AS platform,
    c.name              AS country,
    c.region            AS region,
    l.name              AS language,
    cat.name            AS category,
    g.name              AS genre,
    dt.name             AS device_type,
    v.sound_type        AS sound_type,
    tt.name             AS trend_type,
    v.publish_dayofweek AS publish_dayofweek,
    s.name              AS season,
    a.author_handle     AS author_handle,
    v.music_track       AS music_track,
    a.creator_tier      AS creator_tier,
    v.traffic_source    AS traffic_source,
    v.duration_sec,
    v.views,
    v.likes,
    v.comments,
    v.shares,
    v.saves,
    v.dislikes,
    v.engagement_rate,
    v.engagement_velocity,
    v.engagement_total,
    v.completion_rate,
    v.avg_watch_time_sec,
    v.comment_ratio,
    v.share_rate,
    v.save_rate,
    v.like_dislike_ratio,
    v.like_rate,
    v.dislike_rate,
    v.engagement_per_1k,
    v.trend_duration_days,
    v.upload_hour,
    v.is_weekend,
    v.title_length,
    v.has_emoji
FROM video v
JOIN platform       p   ON v.platform_fk       = p.id
JOIN country        c   ON v.country_fk         = c.id
JOIN language        l   ON v.language_fk        = l.id
JOIN category        cat ON v.category_fk        = cat.id
JOIN genre          g   ON v.genre_fk           = g.id
JOIN device_type    dt  ON v.device_type_fk     = dt.id
JOIN trend_type     tt  ON v.trend_type_fk      = tt.id
JOIN season         s   ON v.season_fk          = s.id
JOIN author         a   ON v.author_fk          = a.id
ORDER BY v.id ASC
"""
        result = self.connection.execute(text(query))
        self.db_df = pd.DataFrame(result.fetchall())
        self.db_df.columns = list(result.keys())

    def test_columns(self):
        csv_cols = [
            'platform', 'country', 'region', 'language', 'category', 'genre',
            'device_type', 'sound_type', 'trend_type', 'publish_dayofweek',
            'season', 'author_handle', 'music_track', 'creator_tier', 'traffic_source',
            'duration_sec', 'views', 'likes', 'comments', 'shares', 'saves', 'dislikes',
            'engagement_rate', 'engagement_velocity', 'engagement_total',
            'completion_rate', 'avg_watch_time_sec', 'comment_ratio', 'share_rate',
            'save_rate', 'like_dislike_ratio', 'like_rate', 'dislike_rate',
            'engagement_per_1k', 'trend_duration_days', 'upload_hour',
            'is_weekend', 'title_length', 'has_emoji'
        ]
        self.assertListEqual(csv_cols, list(self.db_df.columns))

    def test_row_count(self):
        self.assertEqual(len(self.df), len(self.db_df))

    def test_dataframes(self):
        csv_cols = [
            'platform', 'country', 'region', 'language', 'category', 'genre',
            'device_type', 'sound_type', 'trend_type', 'publish_dayofweek',
            'season', 'author_handle', 'music_track', 'creator_tier', 'traffic_source',
            'duration_sec', 'views', 'likes', 'comments', 'shares', 'saves', 'dislikes',
            'engagement_rate', 'engagement_velocity', 'engagement_total',
            'completion_rate', 'avg_watch_time_sec', 'comment_ratio', 'share_rate',
            'save_rate', 'like_dislike_ratio', 'like_rate', 'dislike_rate',
            'engagement_per_1k', 'trend_duration_days', 'upload_hour',
            'is_weekend', 'title_length', 'has_emoji'
        ]
        df_compare = self.df[csv_cols].reset_index(drop=True)
        db_compare = self.db_df[csv_cols].reset_index(drop=True)
        assert_frame_equal(df_compare, db_compare, check_dtype=False)

    def test_no_nulls_in_key_columns(self):
        key_cols = ['platform', 'country', 'language', 'category', 'views', 'engagement_rate']
        for col in key_cols:
            null_count = self.db_df[col].isnull().sum()
            self.assertEqual(null_count, 0, f"NULL vrijednosti pronađene u stupcu: {col}")

    def test_views_positive(self):
        self.assertTrue((self.db_df['views'] > 0).all(), "Postoje redovi s views <= 0")

    def test_engagement_rate_range(self):
        self.assertTrue((self.db_df['engagement_rate'] >= 0).all(), "Negativan engagement_rate")
        self.assertTrue((self.db_df['engagement_rate'] <= 1).all(), "engagement_rate veći od 1")

    def test_platform_values(self):
        valid = {'TikTok', 'YouTube'}
        actual = set(self.db_df['platform'].unique())
        self.assertTrue(actual.issubset(valid), f"Neočekivane platforme: {actual - valid}")

    def test_dimension_counts(self):
        dims = [
            'platform', 'country', 'language', 'category',
            'genre', 'device_type', 'trend_type', 'season', 'author'
        ]
        for dim in dims:
            count = self.connection.execute(text(f"SELECT COUNT(*) FROM {dim}")).scalar()
            self.assertGreater(count, 0, f"Dimenzijska tablica '{dim}' je prazna!")

    def tearDown(self):
        self.connection.close()

if __name__ == '__main__':
    unittest.main()
