from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Enum

engine = create_engine('sqlite:///se.sqlite', echo=True)
Base = declarative_base()

class Winner(Base):
  __tablename__ = 'sebango'

  id = Column(Integer, primary_key=True)
  hcode = Column(String)
  se = Column(String)
  scode = Column(String)
  sname = Column(String)

  def __repr__(self):
    return ""\
        % (self.hcode, self.se, self.scode, self.sname)

def main():
  Base.metadata.create_all(engine)

if __name__ == '__main__':
  main()
