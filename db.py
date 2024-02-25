from typing import List
from sqlalchemy import create_engine, Column, Integer, Text, String, DateTime, Sequence, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from gsmmodem.modem import ReceivedSms as GsmSms
from gsmmodem.modem import Call as GsmCall

from datetime import datetime

Base = declarative_base()

class Sms(Base):
    __tablename__ = 'sms'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    text = Column(Text)
    from_number = Column(String(32))
    time = Column(DateTime)

class Call(Base):
    __tablename__ = 'call'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    from_number = Column(String(32))
    time = Column(DateTime, default=datetime.utcnow, server_default=text("(now())"))

class Db:
    def __init__(self, filename: str):
        engine = create_engine(f'sqlite:///{filename}')
        Base.metadata.create_all(engine)
        self.session = sessionmaker(bind=engine)()
    
    def add_sms(self, sms: GsmSms):
        self.session.add(Sms(text=sms.text, time=sms.time, from_number=sms.number))
        self.session.commit()
    
    def add_call(self, call: GsmCall):
        self.session.add(Call(from_number=call.number))
        self.session.commit()
