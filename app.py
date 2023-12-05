#!.venv/bin/python
from flask import Flask
from utils import ReverseProxied, r
from models import db
import config


app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config.from_object(config)
db.init_app(app)


from v1.views import v1
app.register_blueprint(v1, url_prefix='/v1')


from werkzeug.exceptions import HTTPException
# @app.errorhandler(Exception)
@app.errorhandler(HTTPException)
def error_handler(e):
    if isinstance(e, HTTPException):
        return r(e.code, e.description)
    return r(500, str(e))


@app.route('/')
def index():
    return r(msg='Welcome!')


# flask initdb --drop
from models import User, Application, Book, Account, Category, Tag, Tally
import click
import time
@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')

    # add user
    user = User()._set({
        'mobile': '13530582058',
        'mail': 'binbr@163.com',
        'password': 'YzQyMjJlMmVlN2QyZTM3NjViZjRkNWQ5ZGQwNjQyMTA=',
        'wx_openid': 'ouofN5UNfw331QGE3zvZq_TqEk7k',
        'nick_name': '燃星之曲',
        'avatar_url': '//game.gtimg.cn/images/yxzj/coming/v2/skins/image/20230223/16771367512088.jpg',
        'motto': '别想一下造出大海，请先由小河川开始。',
        'vip_level': 8
    })

    # add apps
    apps = [Application()._set({'app_id': i[0], 'app_name': i[1], 'secret_key': i[2]}) for i in (
        ('wx65c7fff6a12a1e2b','微信小程序','c0506c6421e192a6418fa0bf7e0e65a7'),
        ('wb9705eb7ac2c98403','Web页','2567a5ec9705eb7ac2c984033e06189d'),
    )]

    # add accounts
    accounts = [Account(name=i, user_id=user.id) for i in ('现金钱包','支付宝','微信')]
    db.session.add_all(accounts)

    # add books
    book = [Book(name=i[0], remark=i[1]) for i in (
        ('生活账本', '记录生活的点点滴滴'),
        ('人情账本', '人情请适度，礼轻情谊重'),
    )]
    db.session.add_all(book)
    user.books.append(book[0])
    user.books.append(book[1])
    book[0].accounts.append(accounts[0])
    book[0].accounts.append(accounts[1])
    book[0].accounts.append(accounts[2])
    # book[1].accounts.append(account[0])
    db.session.flush()

    # add categories
    categories = ((
        ('支出', -1, ('餐饮美食','生活日用','服饰美容','休闲玩乐','教育运动','家居家电','交通出行','房租水电','人情社交','其他支出')),
        ('收入', 1, ('工资薪酬','生意投资','奖金补贴','人情社交','其他收入')),
        ('不记收支', 0, ('借款还款','转账')),
    ), (
        ('随礼', -1,),
        ('宴请', 1,),
    ))
    for index, i in enumerate(categories):
        for j in i:
            tmp = Category(pid=None, name=j[0], type=j[1])
            book[index].categories.append(tmp)
            db.session.add(tmp)
            db.session.flush()
            if len(j) == 3:
                db.session.add_all([Category(pid=tmp.id, name=k, type=tmp.type) for k in j[2]])

    # add tags
    tags = (
        (book[1], ('亲友圈', ('张三', '李四', '王五', '赵六', '麻七'))),
    )
    for i in tags:
        tmp = Tag(pid=None, name=i[1][0])
        i[0].tags.append(tmp)
        db.session.add(tmp)
        db.session.flush()
        if len(i[1]) == 2:
            db.session.add_all([Tag(pid=tmp.id, name=j) for j in i[1][1]])

    # add tallies
    tallies = (
        (book[0].id, ((150.50,2,1),(800.80,3,2),(2580,7,3),(8500,13,2),(1200,15,3),),),
        (book[1].id, ((1000,21,None),(60000,22,None),),),
    )
    for i in tallies:
        db.session.add_all([
            Tally(book_id=i[0],amount=j[0], category_id=j[1], account_id=j[2], record_timestamp=int(time.time())) for j in i[1]
        ])

    db.session.commit()


if __name__ == '__main__':
    app.run()
