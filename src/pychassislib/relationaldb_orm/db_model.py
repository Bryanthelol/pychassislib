from sqlalchemy import Column, DateTime, Boolean, func
from sqlalchemy.orm import Query
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

BaseModel = declarative_base()
metadata = BaseModel.metadata


class BaseCrud(BaseModel):

    __abstract__ = True

    # 硬删除
    def delete(self, session, commit=False):
        session.delete(self)
        if commit:
            session.commit()

    # 查
    @classmethod
    def get(cls, session, start=None, count=None, one=True, **kwargs):
        if one:
            return session.query(cls).filter().filter_by(**kwargs).first()
        return session.query(cls).filter().filter_by(**kwargs).offset(start).limit(count).all()

    @classmethod
    def filtered_query(cls, session, filter_args=None, filter_kwargs=None) -> Query:
        if not filter_args:
            filter_args = []
        if not filter_kwargs:
            filter_kwargs = {}
        return session.query(cls).filter(*filter_args).filter_by(**filter_kwargs)

    # 增
    @classmethod
    def create(cls, session, **kwargs):
        one = cls()
        for key in kwargs.keys():
            if hasattr(one, key):
                setattr(one, key, kwargs[key])
        session.add(one)
        if kwargs.get("commit") is True:
            session.commit()
        return one

    def update(self, session, **kwargs):
        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        session.add(self)
        if kwargs.get("commit") is True:
            session.commit()
        return self


class InfoCrud(BaseModel):
    """
    提供软删除，及创建时间，更新时间信息的crud model
    """

    __abstract__ = True

    create_time = Column(DateTime(), default=func.now())
    update_time = Column(DateTime(), default=func.now(), onupdate=func.now())
    delete_time = Column(DateTime())
    is_deleted = Column(Boolean, nullable=False, default=False)

    # 软删除
    def delete(self, session, commit=False):
        self.delete_time = datetime.now()
        self.is_deleted = True
        session.add(self)
        if commit:
            session.commit()

    # 硬删除
    def hard_delete(self, session, commit=False):
        session.delete(self)
        if commit:
            session.commit()

    # 查
    @classmethod
    def get(cls, session, start=None, count=None, one=True, **kwargs):
        if kwargs.get('is_deleted') is None:
            kwargs['is_deleted'] = False
        if one:
            return session.query(cls).filter().filter_by(**kwargs).first()
        return session.query(cls).filter().filter_by(**kwargs).offset(start).limit(count).all()

    @classmethod
    def filtered_query(cls, session, filter_args=None, filter_kwargs=None) -> Query:
        if not filter_args:
            filter_args = []
        if not filter_kwargs:
            filter_kwargs = {}
        return session.query(cls).filter(*filter_args).filter_by(**filter_kwargs)

    # 增
    @classmethod
    def create(cls, session, **kwargs):
        one = cls()
        for key in kwargs.keys():
            if hasattr(one, key):
                setattr(one, key, kwargs[key])
        session.add(one)
        if kwargs.get('commit') is True:
            session.commit()
        return one

    def update(self, session, **kwargs):
        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        session.add(self)
        if kwargs.get('commit') is True:
            session.commit()
        return self