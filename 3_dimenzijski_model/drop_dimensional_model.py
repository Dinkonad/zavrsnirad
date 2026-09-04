from sqlalchemy import create_engine
from generate_star_schema import Base

DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/zavrsni_rad_starshema"
engine = create_engine(DATABASE_URL, echo=True)

Base.metadata.drop_all(engine)

print("Uspješno obrisano.")
