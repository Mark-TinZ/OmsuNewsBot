from re import T
from tokenize import group
import sqlalchemy as sa
import sqlalchemy.orm as sorm

Base = sorm.declarative_base()

class User(Base):
	__tablename__ = "user"

	id_ = sa.Column("id", sa.Integer, primary_key=True)
	tg_id = sa.Column(sa.BigInteger, nullable=False)
	role_id = sa.Column(sa.String(64), nullable=False, default="")
	settings =  sa.Column(sa.JSON(), default=dict())

class Teacher(Base):
	__tablename__ = "teacher"

	id_ = sa.Column("id", sa.Integer, primary_key=True)
	user_id = sa.Column(sa.ForeignKey(User.id_), nullable=True)
	name = sa.Column(sa.String(256), nullable=False)
	tg_authkey = sa.Column(sa.String(256), nullable=True)
	is_sick = sa.Column(sa.Boolean, nullable=False, default=False)
	is_fired = sa.Column(sa.Boolean, nullable=False, default=False)


class Group(Base):
	__tablename__ = "group"

	id_ = sa.Column("id", sa.Integer, primary_key=True)
	name = sa.Column(sa.String(256), nullable=False)
	course_number = sa.Column(sa.Integer, nullable=False)
	is_enabled = sa.Column(sa.Boolean, nullable=False, default=True)

class Student(Base):
	__tablename__ = "student"

	id_ = sa.Column("id", sa.Integer, primary_key=True)
	user_id = sa.Column(sa.ForeignKey(User.id_), unique=True)
	group_id = sa.Column(sa.ForeignKey(Group.id_))
	is_moderator = sa.Column(sa.Boolean, nullable=False, default=False)


class Subject(Base):
	__tablename__ = "subject"

	id_ = sa.Column("id", sa.Integer, primary_key=True)
	name = sa.Column(sa.String(256), nullable=False)
	course_number =  sa.Column(sa.ARRAY(sa.Integer), nullable=False)
	group_id = sa.Column(sa.ARRAY(sa.Integer), nullable=False)
	teacher_id = sa.Column(sa.ARRAY(sa.Integer) , nullable=True)


class Lesson(Base):
	__tablename__ = "lesson"

	id_ = sa.Column("id", sa.Integer, primary_key=True)
	subject_id = sa.Column(sa.ForeignKey(Subject.id_), nullable=False)
	lesson_number = sa.Column(sa.Integer, nullable=False)
	teacher_id = sa.Column(sa.ForeignKey(Teacher.id_), nullable=False)
	group_id = sa.Column(sa.ForeignKey(Group.id_), nullable=False)
	weekday = sa.Column(sa.Integer, nullable=False)
	academic_weeks = sa.Column(sa.ARRAY(sa.Integer), nullable=False)
	room = sa.Column(sa.Integer, nullable=False)
	type_lesson = sa.Column(sa.String, nullable=False)



metadata = Base.metadata
