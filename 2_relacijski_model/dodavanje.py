import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.mysql import insert

CSV_FILE_PATH = "social_media_trends_PROCESSED.csv"
df = pd.read_csv(CSV_FILE_PATH, delimiter=',')
print(f"CSV size: {df.shape}")
print(df.head())

Base = declarative_base()
class Platform(Base):
    __tablename__ = 'platform'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    region = Column(String(50), nullable=False)

class Language(Base):
    __tablename__ = 'language'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

class Genre(Base):
    __tablename__ = 'genre'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

class DeviceType(Base):
    __tablename__ = 'device_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    brand = Column(String(50))

class TrendType(Base):
    __tablename__ = 'trend_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_handle = Column(String(100), nullable=False, unique=True)
    creator_tier = Column(String(50))

class Season(Base):
    __tablename__ = 'season'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)

class Video(Base):
    __tablename__ = 'video'
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform_fk = Column(Integer, ForeignKey('platform.id'))
    country_fk = Column(Integer, ForeignKey('country.id'))
    language_fk = Column(Integer, ForeignKey('language.id'))
    category_fk = Column(Integer, ForeignKey('category.id'))
    genre_fk = Column(Integer, ForeignKey('genre.id'))
    device_type_fk = Column(Integer, ForeignKey('device_type.id'))
    trend_type_fk = Column(Integer, ForeignKey('trend_type.id'))
    author_fk = Column(Integer, ForeignKey('author.id'))
    season_fk = Column(Integer, ForeignKey('season.id'))
    hashtag = Column(String(100))
    title_keywords = Column(String(200))
    sound_type = Column(String(50))
    music_track = Column(String(100))
    week_of_year = Column(Integer)
    duration_sec = Column(Integer)
    views = Column(Integer)
    likes = Column(Integer)
    comments = Column(Integer)
    shares = Column(Integer)
    saves = Column(Integer)
    dislikes = Column(Integer)
    engagement_rate = Column(Float)
    trend_label = Column(String(50))
    source_hint = Column(String(100))
    upload_hour = Column(Integer)
    trend_duration_days = Column(Integer)
    engagement_velocity = Column(Float)
    comment_ratio = Column(Float)
    share_rate = Column(Float)
    save_rate = Column(Float)
    like_dislike_ratio = Column(Float)
    publish_dayofweek = Column(String(20))
    publish_period = Column(String(20))
    event_season = Column(String(50))
    tags = Column(String(200))
    creator_avg_views = Column(Float)
    publish_date_approx = Column(String(20))
    year_month = Column(String(20))
    title = Column(String(200))
    title_length = Column(Integer)
    has_emoji = Column(Integer)
    avg_watch_time_sec = Column(Float)
    completion_rate = Column(Float)
    traffic_source = Column(String(50))
    is_weekend = Column(Integer)
    row_id = Column(String(50))
    engagement_total = Column(Integer)
    like_rate = Column(Float)
    dislike_rate = Column(Float)
    engagement_per_1k = Column(Float)
    engagement_like_rate = Column(Float)
    engagement_comment_rate = Column(Float)
    engagement_share_rate = Column(Float)


DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/zavrsni_rad"
server_engine = create_engine("mysql+pymysql://root:root@localhost:3306/")
with server_engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS zavrsni_rad"))
    conn.commit()
engine = create_engine(DATABASE_URL, echo=False)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
print("Database connected successfully!")
print("Inserting platform...")
platforms = df[['platform']].drop_duplicates().rename(columns={'platform': 'name'})
session.execute(insert(Platform), platforms.to_dict(orient="records"))
session.commit()
platform_map = {p.name: p.id for p in session.query(Platform).all()}

print("Inserting country...")
countries = df[['country', 'region']].drop_duplicates(subset=['country'])
countries_list = [{'name': r['country'], 'region': r['region']} for _, r in countries.iterrows()]
session.execute(insert(Country), countries_list)
session.commit()
country_map = {c.name: c.id for c in session.query(Country).all()}

print("Inserting language...")
languages = df[['language']].drop_duplicates().rename(columns={'language': 'name'})
session.execute(insert(Language), languages.to_dict(orient="records"))
session.commit()
language_map = {l.name: l.id for l in session.query(Language).all()}

print("Inserting category...")
categories = df[['category']].drop_duplicates().rename(columns={'category': 'name'})
session.execute(insert(Category), categories.to_dict(orient="records"))
session.commit()
category_map = {c.name: c.id for c in session.query(Category).all()}

print("Inserting genre...")
genres = df[['genre']].drop_duplicates().rename(columns={'genre': 'name'})
session.execute(insert(Genre), genres.to_dict(orient="records"))
session.commit()
genre_map = {g.name: g.id for g in session.query(Genre).all()}

print("Inserting device type...")
device_types = df[['device_type', 'device_brand']].drop_duplicates(subset=['device_type'])
device_types_list = [{'name': r['device_type'], 'brand': r['device_brand']} for _, r in device_types.iterrows()]
session.execute(insert(DeviceType), device_types_list)
session.commit()
device_map = {d.name: d.id for d in session.query(DeviceType).all()}

print("Inserting trend type...")
trend_types = df[['trend_type']].drop_duplicates().rename(columns={'trend_type': 'name'})
session.execute(insert(TrendType), trend_types.to_dict(orient="records"))
session.commit()
trend_map = {t.name: t.id for t in session.query(TrendType).all()}

print("Inserting authors...")
authors = df[['author_handle', 'creator_tier']].drop_duplicates(subset=['author_handle'])
authors_list = [{'author_handle': r['author_handle'], 'creator_tier': r['creator_tier']} for _, r in authors.iterrows()]
session.execute(insert(Author), authors_list)
session.commit()
author_map = {a.author_handle: a.id for a in session.query(Author).all()}

print("Inserting seasons...")
seasons = df[['season']].drop_duplicates().rename(columns={'season': 'name'})
session.execute(insert(Season), seasons.to_dict(orient="records"))
session.commit()
season_map = {s.name: s.id for s in session.query(Season).all()}


print("Processing videos...")

video_data = df.copy()

video_data['platform_fk'] = video_data['platform'].map(platform_map)
video_data['country_fk'] = video_data['country'].map(country_map)
video_data['language_fk'] = video_data['language'].map(language_map)
video_data['category_fk'] = video_data['category'].map(category_map)
video_data['genre_fk'] = video_data['genre'].map(genre_map)
video_data['device_type_fk'] = video_data['device_type'].map(device_map)
video_data['trend_type_fk'] = video_data['trend_type'].map(trend_map)
video_data['author_fk'] = video_data['author_handle'].map(author_map)
video_data['season_fk'] = video_data['season'].map(season_map)

video_data = video_data.drop(columns=[
    'platform', 'country', 'region', 'language', 'category', 'genre',
    'device_type', 'device_brand', 'trend_type', 'author_handle',
    'creator_tier', 'season', 'notes', 'sample_comments'
])

session.execute(insert(Video), video_data.to_dict(orient="records"))
session.commit()

print("Data imported successfully!")

session.close()
