from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///todoai_app.db" #db kodda olusturulcak demek //dan sonrasi da adi

engine = create_engine( #naisl baglanti acilacak
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #bu engine ile session(baglanti) acar
Base = declarative_base()  #bu kullanilacak kolon vs olustururken



