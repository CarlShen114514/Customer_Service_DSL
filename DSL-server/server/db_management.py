from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# 创建数据库引擎
engine = create_engine('mysql://admin:cde3xsw2zaq1@localhost/mydb', echo=True)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<User(username='{self.username}', password='{self.password}')>"


Base.metadata.create_all(engine)

SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

def add_user(username, password):
    session = Session()
    # 检查用户名是否已存在
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user:
        session.close()
        return False
    
    new_user = User(username=username, password=password)
    session.add(new_user)
    session.commit()
    session.close()
    return True


def get_user(username, password):
    session = Session()
    user = session.query(User).filter_by(username=username, password=password).first()
    session.close()
    return user

def get_all_users():
    session = Session()
    users = session.query(User).all()
    session.close()
    return users
