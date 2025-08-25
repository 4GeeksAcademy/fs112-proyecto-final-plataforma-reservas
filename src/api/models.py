from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, DateTime, Date, ForeignKey, Integer, String, Text, DECIMAL, func, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional



#########################################################################################
#########################################################################################
#############                            TABLES                             #############
#############                      Company: WEPLACEIT                       #############
#############                       with SQL Alchemy                        #############
#########################################################################################
#########################################################################################

# class Base(DeclarativeBase):
#     pass

db = SQLAlchemy()

############################################
###########         USER         ###########
############################################

class User(db.Model):
    __tablename__ = "user"


    ### ATTRIBUTES ###
    id:         Mapped[int]      = mapped_column( Integer,     primary_key=True,                     autoincrement=True)
    email:      Mapped[str]      = mapped_column( String(40),  unique=True,         nullable=False)
    username:   Mapped[str]      = mapped_column( String(40),  unique=True,         nullable=False)
    first_name: Mapped[str]      = mapped_column( String(40),                       nullable=False)
    last_name:  Mapped[str]      = mapped_column( String(40),                       nullable=False)
    password:   Mapped[str]      = mapped_column( String(255),                      nullable=False)
    is_active:  Mapped[bool]     = mapped_column( Boolean,     default=True,        nullable=False)
    created_at: Mapped[datetime] = mapped_column( DateTime,    default=func.now(),  nullable=False)


    ### RELATIONS ###

    # One-to-many relationship with Space (owner) --> shows the amount of spaces owned by the user
    owned_spaces: Mapped[List["Space"]] = relationship(
        "Space", 
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    # One-to-many relationship with Booking (guest) --> shows the amount of bookings this user has
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking", 
        back_populates="guest",
        cascade="all, delete-orphan"
    )


    ### SERIALIZATION ###
    def serialize(self):
        return {
            "user_id":    self.id,
            "email":      self.email,
            "username":   self.username,
            "first_name": self.first_name,
            "last_name":  self.last_name,
            "is_active":  self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


     ### __repr__ METHOD ###
    def __repr__(self):
        return f"<User ID {self.id} | Username: {self.username} | Email: {self.email} | Name: {self.first_name} {self.last_name}>"



############################################
##########         Spaces         ##########
############################################

class Space(db.Model):
    __tablename__ = "space"


    ### ATTRIBUTES ###

    id:            Mapped[int]      = mapped_column( Integer,       primary_key=True,                      autoincrement=True)
    owner_id:      Mapped[int]      = mapped_column( Integer,       ForeignKey("user.id",                  ondelete="CASCADE"), 
                                                                                          nullable=False)    
    title:         Mapped[str]      = mapped_column( String(60),                          nullable=False)
    address:       Mapped[str]      = mapped_column( String(255),                         nullable=False)
    description:   Mapped[str]      = mapped_column( Text,                                nullable=True)
    price_per_day: Mapped[Decimal]  = mapped_column( DECIMAL(10, 2),                      nullable=False)
    capacity:      Mapped[int]      = mapped_column( Integer,                             nullable=False)
    created_at:    Mapped[datetime] = mapped_column( DateTime,      default=func.now(),   nullable=False)
    updated_at:    Mapped[datetime] = mapped_column( DateTime,      default=func.now(),   nullable=False,  onupdate=func.now())


    ### TABLE CONSTRAINTS ###
    __table_args__ = (
        CheckConstraint('capacity > 0',      name='check_positive_capacity'),
        CheckConstraint('price_per_day > 0', name='check_positive_price'),
    )


    ### RELATIONS ###

    # Many-to-one relationship with User (owned_spaces) --> shows the user owner of the space
    owner: Mapped["User"] = relationship(
        "User", 
        back_populates="owned_spaces"
    )

    # One-to-many relationship with Booking --> shows all the bookings related to a particular space
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking", 
        back_populates="space",
        cascade="all, delete-orphan"
    )


    ### SERIALIZATION ###
    def serialize(self):
        return {
            "space_id":      self.id,
            "owner_id":      self.owner_id,
            "title":         self.title,
            "address":       self.address,
            "description":   self.description,
            "price_per_day": float(self.price_per_day),
            "capacity":      self.capacity,
            "created_at":    self.created_at.isoformat() if self.created_at else None,
            "updated_at":    self.updated_at.isoformat() if self.updated_at else None
        }


     ### __repr__ METHOD ###
    def __repr__(self):
        return f"<Space ID {self.id} | Title: {self.title} | Price per day: {self.price_per_day} | Capacity: {self.capacity}>"



############################################
##########        Bookings        ##########
############################################

class Booking(db.Model):
    __tablename__ = "booking"
    

    ### ATTRIBUTES ###
    id:  Mapped[int]              = mapped_column( Integer,       primary_key=True,                       autoincrement=True)
    guest_id:    Mapped[int]      = mapped_column( Integer,       ForeignKey("user.id",                   ondelete="CASCADE"), 
                                                                                         nullable=False)   
    space_id:    Mapped[int]      = mapped_column( Integer,       ForeignKey("space.id",                  ondelete="CASCADE"), 
                                                                                         nullable=False)   
    check_in:    Mapped[date]     = mapped_column( Date,                                 nullable=False)   
    check_out:   Mapped[date]     = mapped_column( Date,                                 nullable=False)   
    total_days:  Mapped[int]      = mapped_column( Integer,                              nullable=False)   
    status:      Mapped[str]      = mapped_column( String(40),                           nullable=False)    
    total_price: Mapped[Decimal]  = mapped_column( DECIMAL(10,2),                        nullable=False)   
    created_at:  Mapped[datetime] = mapped_column( DateTime,                             nullable=False,   default=func.now()) 
        

    ### TABLE CONSTRAINTS ###
    __table_args__ = (
        CheckConstraint('check_out   > check_in', name='check_valid_booking_dates'),
        CheckConstraint('total_days  > 0',        name='check_positive_days'),
        CheckConstraint('total_price > 0',        name='check_positive_total_price'),

        # How to prevent double bookings for the same space and dates????
        # UniqueConstraint('space_id', 'check_in', 'check_out', name='unique_booking_dates'),   ### ---> Like this?
    )


    ### RELATIONS ###

    # Many-to-one relationship with User (bookings) --> shows the user that booked a particular space
    guest: Mapped["User"] = relationship(
        "User",
        back_populates="bookings"
    )

    # Many-to-one relationship with Space --> shows the particular space being booked
    space: Mapped["Space"] = relationship(
        "Space",
        back_populates="bookings"
    )

    # One-to-one relationship with Payment --> shows the payment for this booking
    payment: Mapped[Optional["Payment"]] = relationship(
        "Payment", 
        back_populates="booking",
        cascade="all, delete-orphan",
        uselist=False
    )


    ### SERIALIZATION ###
    def serialize(self):
        return {
            "booking_id":  self.id,
            "guest_id":    self.guest_id,
            "space_id":    self.space_id,
            "check_in":    self.check_in.isoformat()  if self.check_in  else None,
            "check_out":   self.check_out.isoformat() if self.check_out else None,
            "total_days":  self.total_days,
            "status":      self.status,
            "total_price": float(self.total_price),
            "created_at":  self.created_at.isoformat() if self.created_at else None
        }


     ### __repr__ METHOD ###
    def __repr__(self):
        return f"<Booking ID:{self.id} | Guest ID:{self.guest_id} | Space ID:{self.space_id} | Dates: from {self.check_in} to {self.check_out} | Status: {self.status}>"



############################################
##########        Payments        ##########
############################################

class Payment(db.Model):
    __tablename__ = "payment"
    

    ### ATTRIBUTES ###
    id:             Mapped[int]      = mapped_column( Integer,  primary_key=True,                        autoincrement=True)
    booking_id:     Mapped[int]      = mapped_column( Integer,  ForeignKey("booking.id",                 ondelete="CASCADE"), 
                                                                unique=True, # One payment per booking
                                                                                        nullable=False)
    amount:         Mapped[Decimal]  = mapped_column( DECIMAL(10, 2),                   nullable=False)
    currency:       Mapped[str]      = mapped_column( String(3),                        nullable=False)
    payment_method: Mapped[str]      = mapped_column( String(40),                       nullable=False)
    paid_at:        Mapped[datetime] = mapped_column( DateTime,                         nullable=False,   default=func.now())


    ### TABLE CONSTRAINTS ###
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_positive_amount'),
    )


    ### RELATIONS ###

    # One-to-one relationship with Booking --> shows the booking related to this payment
    booking: Mapped["Booking"] = relationship(
        "Booking",
        back_populates="payment"
    )


    ### SERIALIZATION ###
    def serialize(self):
        return {
            "payment_id":     self.id,
            "booking_id":     self.booking_id,
            "amount":         float(self.amount),
            "currency":       self.currency,
            "payment_method": self.payment_method,
            "paid_at":        self.paid_at.isoformat() if self.paid_at else None
        }


     ### __repr__ METHOD ###
    def __repr__(self):
        return f"<Payment ID {self.id} | Booking ID:{self.booking_id} | Amount:{self.amount} {self.currency} | Payment method:{self.payment_method}>"


