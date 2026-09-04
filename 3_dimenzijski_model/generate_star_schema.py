import sys
sys.stdout.reconfigure(encoding='utf-8')

from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Float, DateTime, ForeignKey, text
from sqlalchemy.orm import declarative_base


DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/zavrsni_rad_starshema"


server_engine = create_engine("mysql+pymysql://root:root@localhost:3306/")
with server_engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS zavrsni_rad_starshema"))
    conn.commit()

engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()

class DimCreator(Base):
    __tablename__ = 'dim_creator'

    creator_tk = Column(BigInteger, primary_key=True)

    version = Column(Integer)
    date_from = Column(DateTime)
    date_to = Column(DateTime)

    author_handle = Column(String(100))
    creator_tier = Column(String(50))
    creator_avg_views = Column(Float)


class DimContent(Base):
    __tablename__ = 'dim_content'

    content_tk = Column(BigInteger, primary_key=True)

    category = Column(String(100))
    genre = Column(String(100))
    hashtag = Column(String(100))
    tags = Column(String(200))


class DimTime(Base):
    __tablename__ = 'dim_time'

    time_tk = Column(Integer, primary_key=True, autoincrement=True)

    year_month = Column(String(20))
    week_of_year = Column(Integer)
    publish_dayofweek = Column(String(20))
    upload_hour = Column(Integer)


class DimPlatform(Base):
    __tablename__ = 'dim_platform'

    platform_tk = Column(Integer, primary_key=True, autoincrement=True)

    platform = Column(String(50))


class DimLocation(Base):
    __tablename__ = 'dim_location'

    location_tk = Column(Integer, primary_key=True, autoincrement=True)

    country = Column(String(100))
    region = Column(String(100))
    language = Column(String(50))


class DimDevice(Base):
    __tablename__ = 'dim_device'

    device_tk = Column(Integer, primary_key=True, autoincrement=True)

    device_type = Column(String(50))
    device_brand = Column(String(50))
    traffic_source = Column(String(50))


class FactEngagement(Base):
    __tablename__ = 'fact_engagement'

    fact_tk = Column(BigInteger, primary_key=True)

    creator_tk = Column(BigInteger, ForeignKey('dim_creator.creator_tk'))
    content_tk = Column(BigInteger, ForeignKey('dim_content.content_tk'))
    time_tk = Column(Integer, ForeignKey('dim_time.time_tk'))
    platform_tk = Column(Integer, ForeignKey('dim_platform.platform_tk'))
    location_tk = Column(Integer, ForeignKey('dim_location.location_tk'))
    device_tk = Column(Integer, ForeignKey('dim_device.device_tk'))

    row_id = Column(String(50))

    views = Column(BigInteger)
    likes = Column(BigInteger)
    comments = Column(BigInteger)
    shares = Column(BigInteger)
    saves = Column(BigInteger)
    engagement_total = Column(BigInteger)
    engagement_rate = Column(Float)
    avg_watch_time_sec = Column(Float)
    completion_rate = Column(Float)

    like_rate = Column(Float)
    share_rate = Column(Float)
    comment_rate = Column(Float)
    is_high_engagement = Column(Integer)
    duration_sec = Column(Integer)


Base.metadata.create_all(engine)

print("✅ Baza zavrsni_rad_starshema uspješno kreirana!")
