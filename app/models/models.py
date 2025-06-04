from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from app.database.session import Base

# Связь многие-ко-многим между Organization и Activity
organization_activity = Table(
    'organization_activity',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id')),
    Column('activity_id', Integer, ForeignKey('activities.id'))
)

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
     
    phones = relationship("Phone", back_populates="organization")
    building_id = Column(Integer, ForeignKey("buildings.id"))
    building = relationship("Building", back_populates="organizations")
    activities = relationship("Activity", secondary=organization_activity, back_populates="organizations")

class Phone(Base):
    __tablename__ = "phones"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
     
    organization = relationship("Organization", back_populates="phones")

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    location = Column(Geography(geometry_type='POINT', srid=4326))
    
     
    organizations = relationship("Organization", back_populates="building")
    
    @property
    def latitude(self):
        if self.location is not None:
            point = to_shape(self.location)
            return point.y
        return 0.0
        
    @property
    def longitude(self):
        if self.location is not None: 
            point = to_shape(self.location)
            return point.x
        return 0.0

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    parent_id = Column(Integer, ForeignKey("activities.id"))
    level = Column(Integer, default=1)  # Уровень вложенности
    
    
    children = relationship("Activity",
                          backref=backref("parent", remote_side=[id]))
    organizations = relationship("Organization", 
                              secondary=organization_activity,
                              back_populates="activities")
