from typing import List, Optional
from typing_extensions import Annotated
from flask_sqlalchemy import SQLAlchemy
from redis import ConnectionPool, StrictRedis
from sqlalchemy import String, Text, SmallInteger, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import re

# Redis连接参数
REDIS_CONFIG = {
    'host': '172.17.0.1',
    'port': 6379,
    'db': 0,
    'decode_responses': True
}

db = SQLAlchemy()

intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
str_name = Annotated[str, mapped_column(String(16), nullable=False, doc='名称')]
str_remark = Annotated[str, mapped_column(String(255), nullable=True, doc='备注')]

class Base(db.Model):
    __abstract__ = True
    __cloumns__ = tuple()

    def _get(self, keys:list|tuple = None):
        def __to_camel(s:str):
            return re.sub(r'(_[a-z])', lambda x: x.group(1)[1].upper(), s.lower())
        ret = {}
        keys = keys or self.__cloumns__
        for k in keys:
            if hasattr(self, k):
                def __get(base: Base):
                    return base._get()
                v = getattr(self, k)
                if isinstance(v, list):
                    v = [__get(i) for i in v]
                elif isinstance(v, Base):
                    v = __get(v)
                ret[__to_camel(k)] = v
        return ret

    def _set(self, kv:dict):
        def __to_snake(s:str):
            return re.sub(r'([a-z])([A-Z])', r'\1_\2', s).lower()
        for k, v in kv.items():
            k = __to_snake(k)
            if hasattr(self, k):
                setattr(self, k, v)
        if not self.id:
            db.session.add(self)
        db.session.commit()
        return self

    def _del(self):
        db.session.delete(self)
        db.session.commit()
        return True


class User(Base):
    __tablename__ = 'user'
    __cloumns__ = ('nick_name', 'avatar_url', 'motto', 'vip_level', 'mobile', 'mail', 'wx_openid', 'accounts', 'books', 'configure')
    id: Mapped[intpk]
    mobile: Mapped[str] = mapped_column(String(11), unique=True, nullable=True, index=True, doc='手机号')
    mail: Mapped[str] = mapped_column(String(64), unique=True, nullable=True, index=True, doc='邮箱')
    wx_openid: Mapped[str] = mapped_column(String(64), unique=True, nullable=True, index=True, doc='微信openid')
    password: Mapped[str] = mapped_column(String(64), nullable=True, doc='密码')
    nick_name: Mapped[str_name]
    avatar_url: Mapped[str] = mapped_column(Text, nullable=True, doc='头像url')
    motto: Mapped[str_remark] = mapped_column(doc='格言')
    vip_level: Mapped[int] = mapped_column(SmallInteger, default=int(1), doc='会员等级')
    created: Mapped[datetime] = mapped_column(default=datetime.now)
    state: Mapped[int] = mapped_column(default=int(0))
    configure: Mapped['UserConfigure'] = relationship('UserConfigure', back_populates='user', uselist=False, cascade='all, delete')
    accounts: Mapped[List['Account']] = relationship(cascade="all, delete") # 1->n 单方向一对多，一方引用多方
    books: Mapped[List['Book']] = relationship(secondary='user_book', cascade="all, delete", back_populates='users') # n->n 多对多，双向引用

class UserConfigure(Base):
    __tablename__ = 'user_configure'
    __cloumns__ = ('current_book_id',)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), primary_key=True) # 1->1
    user = relationship('User', back_populates='configure')
    current_book_id: Mapped[int] = mapped_column(SmallInteger, default=int(0), doc='当前账本')

class Application(Base):
    __tablename__ = 'application'
    __cloumns__ = ('id', 'app_id', 'app_name', 'secret_key', 'expirydate')
    id: Mapped[intpk]
    app_id: Mapped[str] = mapped_column(String(32), unique=True, index=True, doc='AppID')
    app_name: Mapped[str_name]
    secret_key: Mapped[str] = mapped_column(String(64), doc='密钥')
    expirydate: Mapped[datetime]

class Book(Base):
    __tablename__ = 'book'
    __cloumns__ = ('id', 'name', 'icon', 'remark', 'configure', 'accounts', 'categories', 'tags', 'created')
    id: Mapped[intpk]
    name: Mapped[str_name]
    icon: Mapped[str_remark] = mapped_column(doc='图标url')
    remark: Mapped[str_remark]
    created: Mapped[datetime] = mapped_column(default=datetime.now)
    state: Mapped[int] = mapped_column(default=int(0))
    configure: Mapped['BookConfigure'] = relationship('BookConfigure', back_populates='book', uselist=False, cascade='all, delete')
    users: Mapped[List['User']] = relationship(secondary='user_book', back_populates='books') # n->n 多对多，双向引用
    accounts: Mapped[List['Account']] = relationship(secondary='book_account') # n->n 多对多，单向引用
    categories: Mapped[List['Category']] = relationship(secondary='book_category', cascade="all, delete") # n->n 多对多，单向引用
    tags: Mapped[List['Tag']] = relationship(secondary='book_tag', cascade="all, delete") # n->n 多对多，单向引用
    tallies: Mapped[List['Tally']] = relationship(lazy='dynamic', cascade="all, delete")

class BookConfigure(Base):
    __tablename__ = 'book_configure'
    __cloumns__ = ('budget', 'period')
    book_id: Mapped[int] = mapped_column(ForeignKey('book.id', ondelete='CASCADE'), primary_key=True) # 1->1
    book = relationship('Book', back_populates='configure')
    budget: Mapped[DECIMAL] = mapped_column(DECIMAL(13, 4), default=0, doc='预算金额')
    period: Mapped[str] = mapped_column(String(32), default='month', doc='AppID')

class Account(Base):
    __tablename__ = 'account'
    __cloumns__ = ('id', 'name', 'icon', 'remark')
    id: Mapped[intpk]
    name: Mapped[str_name]
    icon: Mapped[str_remark] = mapped_column(doc='图标url')
    remark: Mapped[str_remark]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE')) # n->1

class Category(Base):
    __tablename__ = 'category'
    __cloumns__ = ('id', 'pid', 'name', 'type', 'icon', 'remark', 'seq', 'children')
    id: Mapped[intpk]
    name: Mapped[str_name]
    type: Mapped[1|0|-1] = mapped_column(SmallInteger, default=int(0), doc='类型')
    icon: Mapped[str_remark] = mapped_column(doc='图标url')
    remark: Mapped[str_remark]
    seq: Mapped[int] = mapped_column(SmallInteger, default=int(0), doc='序号')
    pid: Mapped[Optional[int]] = mapped_column(ForeignKey('category.id', ondelete='CASCADE'), doc='父ID') # n->1
    children: Mapped[List['Category']] = relationship(cascade="all, delete") # 1->n 单方向一对多，一方引用多方

class Tag(Base):
    __tablename__ = 'tag'
    __cloumns__ = ('id', 'pid', 'name', 'remark', 'seq', 'children')
    id: Mapped[intpk]
    name: Mapped[str_name]
    remark: Mapped[str_remark]
    seq: Mapped[int] = mapped_column(SmallInteger, default=int(0), doc='序号')
    pid: Mapped[Optional[int]] = mapped_column(ForeignKey('tag.id', ondelete='CASCADE'), doc='父ID') # n->1
    children: Mapped[List['Tag']] = relationship(cascade="all, delete") # 1->n 单方向一对多，一方引用多方

class Tally(Base):
    __tablename__ = 'tally'
    __cloumns__ = ('id', 'amount', 'record_timestamp', 'remark', 'category_id', 'account_id', 'tags')
    id: Mapped[intpk]
    amount: Mapped[DECIMAL] = mapped_column(DECIMAL(13, 4), default=0, doc='金额')
    record_timestamp: Mapped[int] = mapped_column(index=True)
    remark: Mapped[str_remark]
    book_id: Mapped[int] = mapped_column(ForeignKey('book.id', ondelete='CASCADE')) # n->1
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id')) # n->1
    account_id: Mapped[Optional[int]] = mapped_column(ForeignKey('account.id')) # n->1
    category: Mapped['Category'] = relationship() # n->1 多方引用一方
    account: Mapped[Optional['Account']] = relationship() # n->1 多方引用一方
    tags: Mapped[List['Tag']] = relationship(secondary='tally_tag') # n->n 多对多，一方引用

class UserBook(db.Model):
    __tablename__ = 'user_book'
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), primary_key=True) # n->n
    book_id: Mapped[int] = mapped_column(ForeignKey('book.id', ondelete='CASCADE'), primary_key=True) # n->n
    permission: Mapped[int] = mapped_column(default=int(4), doc='权限r=4,(w=2,d=1,)rw=6,rwd=7')

class BookAccount(db.Model):
    __tablename__ = 'book_account'
    book_id: Mapped[int] = mapped_column(ForeignKey('book.id', ondelete='CASCADE'), primary_key=True) # n->n
    account_id: Mapped[int] = mapped_column(ForeignKey('account.id', ondelete='CASCADE'), primary_key=True) # n->n

class BookCategory(db.Model):
    __tablename__ = 'book_category'
    book_id: Mapped[int] = mapped_column(ForeignKey('book.id', ondelete='CASCADE'), primary_key=True) # n->n
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete='CASCADE'), primary_key=True) # n->n

class BookTag(db.Model):
    __tablename__ = 'book_tag'
    book_id: Mapped[int] = mapped_column(ForeignKey('book.id', ondelete='CASCADE'), primary_key=True) # n->n
    tag_id: Mapped[int] = mapped_column(ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True) # n->n

class TallyTag(db.Model):
    __tablename__ = 'tally_tag'
    tally_id: Mapped[int] = mapped_column(ForeignKey('tally.id', ondelete='CASCADE'), primary_key=True) # n->n
    tag_id: Mapped[int] = mapped_column(ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True) # n->n


class Permission(Base):
    __tablename__ = 'permission'
    id: Mapped[intpk]
    user_id = mapped_column(ForeignKey('user.id')) # 1->n
    module_name: Mapped[str_name] # book, user, application
    authority: Mapped[int] = mapped_column(default=int(4), doc='权限r=4,(w=2,d=1,)rw=6,rwd=7')
    remark: Mapped[str_remark]


from flask import request
from authlib.jose import jwt, JoseError
from functools import wraps
from werkzeug.exceptions import Unauthorized, NotFound
import requests
import time
class Authorize:
    app: Application
    user: User
    def __init__(self, appid: str = None, **kwargs) -> None:
        self.appid = appid
        if kwargs.get('password'):
            self.user = self.check_password(**kwargs)
        elif kwargs.get('vcode'):
            self.user = self.check_vcode(**kwargs)
        elif kwargs.get('code'):
            self.user = self.check_code(**kwargs)

    @property
    def appid(self):
        return self.__appid
    @appid.setter
    def appid(self, value):
        app = self.get_app(value) if value else None
        if app is None:
            raise Unauthorized('非法客户端')
        self.app = app
        self.__appid = str(value)

    def get_app(self, appid: str) -> Application | None:
        return Application.query.filter_by(app_id=appid).first()

    def generate_token(self):
        if not self.app or not self.user:
            return None
        payload = {
            'aud': self.user.id,
            'exp': int(datetime.timestamp(self.app.expirydate))
        }
        return jwt.encode(
            {'typ': 'JWT', 'alg': 'HS256'},
            payload,
            self.app.secret_key,
        ).decode('ascii')

    def check_password(self, password: str, **kwargs):
        user = User.query.filter_by(**kwargs).first()
        if not user:
            raise NotFound('用户未注册')
        if user.password != self.__md5_base64(password):
            raise Unauthorized('密码错误')
        return user

    def check_vcode(self, vcode: str, **kwargs):
        cache_vcode = Cache().get(kwargs.get('mobile') or kwargs.get('mail'))
        if not cache_vcode:
            raise Unauthorized('验证码无效或过期')
        if vcode != cache_vcode:
            raise Unauthorized('验证码错误')
        user = User.query.filter_by(**kwargs).first()
        return user

    def check_code(self, code: str):
        return User.query.filter_by(wx_openid=self.__get_wx_openid(code)).first()

    def __md5_base64(self, str: str):
        """MD5加密 & Base64"""
        import hashlib, base64
        hmd5 = hashlib.md5(b'perfei#md5')
        hmd5.update(str.encode('utf-8'))
        return base64.b64encode(hmd5.hexdigest().encode('utf-8')).decode()

    def __get_wx_openid(self, js_code:str) -> str | None:
        """通过微信auth.code2Session API 获取openid"""
        req = dict(requests.get('https://api.weixin.qq.com/sns/jscode2session?', {
            'appid': self.app.app_id,
            'secret': self.app.secret_key,
            'js_code': js_code, 
            'grant_type': 'authorization_code'
        }).json())
        if 'errcode' in req and req['errcode'] != 0:
            errmsg = {
                -1: '微信系统繁忙',	
                40029: 'code 无效',
                45011: '请勿频繁操作',
                40226: '微信用户被限制'
            }
            raise Unauthorized(errmsg.get(req['errcode'], '微信验证失败'))
        return req.get('openid')

    @staticmethod
    def login_required(view_func):
        @wraps(view_func)
        def verify_token(*args, **kwargs):
            print(view_func.__name__, request.method)
            app: Application = Application.query.filter_by(app_id=request.headers.get('appid')).first()
            if not app:
                raise Unauthorized('非法客户端')
            try:
                data = jwt.decode(request.headers['Authorization'].split(None, 1)[1], app.secret_key)
            except Exception:
                raise Unauthorized('登录凭证无效')
            if time.time() > data.get('exp', 0): 
                raise Unauthorized('凭证已到期')
            return view_func(*args, user_id=data.get('aud'), **kwargs)
        return verify_token


class Cache:
    redis = None
    def __init__(self) -> None:
        self.redis = StrictRedis(connection_pool=ConnectionPool(**REDIS_CONFIG))

    def get(self, key: str):
        return self.redis.get(key)

    def set(self, key: str, value='', ex=300):
        return self.redis.set(key, value, ex=ex)
