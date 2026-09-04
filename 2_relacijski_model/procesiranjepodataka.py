import pandas as pd

CSV_FILE_PATH = "../1_EDA/youtube-tiktok-shorts.csv"

df = pd.read_csv(CSV_FILE_PATH, delimiter=',')
df = df.drop_duplicates()
df.columns = df.columns.str.lower().str.replace(' ', '_')

string_cols = [
    'platform','country','region','language','category','hashtag','title_keywords','author_handle','sound_type','music_track','trend_label','source_hint','notes',
    'device_type','genre','trend_type','publish_dayofweek','publish_period', 'event_season','tags','sample_comments','creator_tier','season',
    'publish_date_approx','year_month','title','device_brand','traffic_source','row_id'
]
for col in string_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

df['platform'] = df['platform'].replace({
    'tiktok':'TikTok',
    'youtube':'YouTube',
    'TIKTOK':'TikTok',
    'YOUTUBE':'YouTube'
})

df['country'] = df['country'].replace({
    'Jp':'Japan','Se':'Sweden','Za':'South Africa','Kr':'South Korea','Au':'Australia', 'Us':'United States','Gb':'United Kingdom','De':'Germany','Fr':'France','Br':'Brazil',
    'In':'India','Mx':'Mexico','Ca':'Canada','Ng':'Nigeria','Eg':'Egypt','Ar':'Argentina', 'Pk':'Pakistan','Id':'Indonesia','Tr':'Turkey','Th':'Thailand','Ph':'Philippines',
    'Vn':'Vietnam','Pl':'Poland','Nl':'Netherlands','Ru':'Russia','It':'Italy','Es':'Spain','Cn':'China','Sa':'Saudi Arabia','Ae':'United Arab Emirates','Ke':'Kenya','Ma':'Morocco','Co':'Colombia'
})

df['language'] = df['language'].replace({
    'ja':'Japanese','sv':'Swedish','en':'English','ko':'Korean','de':'German','fr':'French', 'pt':'Portuguese','hi':'Hindi','es':'Spanish','ar':'Arabic','tr':'Turkish','th':'Thai',
    'tl':'Filipino','vi':'Vietnamese','pl':'Polish','nl':'Dutch','ru':'Russian','it':'Italian','zh':'Chinese','sw':'Swahili','id':'Indonesian'
})

df['publish_date_approx'] = pd.to_datetime(df['publish_date_approx'], errors='coerce')

df = df[df['views'] > 0]

int_cols = [
    'views','likes','comments','shares','saves','dislikes','duration_sec','upload_hour','trend_duration_days','title_length','has_emoji','is_weekend','engagement_total'
]

for col in int_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('Int64')

float_cols = [
    'engagement_rate','engagement_velocity','comment_ratio','share_rate','save_rate',
    'like_dislike_ratio','creator_avg_views','avg_watch_time_sec','completion_rate',
    'like_rate','dislike_rate','engagement_per_1k','engagement_like_rate',
    'engagement_comment_rate','engagement_share_rate'
]

for col in float_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

df20 = df.sample(frac=0.2, random_state=1)
df80 = df.drop(df20.index)

df80['publish_date_approx'] = df80['publish_date_approx'].dt.strftime('%d.%m.%Y')
df20['publish_date_approx'] = df20['publish_date_approx'].dt.strftime('%d.%m.%Y')

df80.to_csv("social_media_trends_PROCESSED.csv", index=False)
df20.to_csv("social_media_trends_PROCESSED_20.csv", index=False)








