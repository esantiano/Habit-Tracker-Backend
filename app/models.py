from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, func, UniqueConstraint, Index
from sqlalchemy.orm import relationship, as_declarative
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    username = Column(String, nullable=False)
    timezone = Column(String, default="UTC")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("HabitLog", back_populates="user", cascade="all, delete-orphan")

class Habit(Base):
    __tablename__ = "habits"
    __table_args__ = (
        Index("ix_habits_user_archived", "user_id", "is_archived"),
    )
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    goal_type = Column(String, nullable=False)
    target_per_period = Column(Integer, default=1)
    start_date = Column(Date, nullable=False)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="habits")
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")

class HabitLog(Base):
    __tablename__ = "habit_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "habit_id", "date", name="uq_user_habit_date"),
        Index("ix_habit_logs_user_date", "user_id", "date"),
        Index("ix_habit_logs_habit_date", "habit_id", "date"),
    )
    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    value = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    habit = relationship("Habit", back_populates="logs")
    user = relationship("User", back_populates="logs")