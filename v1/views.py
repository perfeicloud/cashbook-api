from flask import Blueprint, request
from models import db, Authorize as auth, User, Application, Book, Account, Category, Tag, Tally, UserBook
from utils import r

v1 = Blueprint('v1', __name__)

# ---------- authorize API ----------
@v1.route('/authorize/login', methods=['POST'])
def user_login():
    '''用户登录'''
    req = dict(request.json)
    token = auth(request.headers.get('appid'), **req).generate_token()
    return r(data={'token': token})


# ---------- my API ----------
@v1.route('/my', methods=['GET'])
@auth.login_required
def my_for_id(user_id:int):
    user: User = User.query.filter_by(id=user_id, state=0).first()
    if not user:
        return r(403, '用户被限制')
    return r(data=user._get())


# ---------- userinfo API ----------
@v1.route('/userinfo', methods=['GET', 'PUT'])
@auth.login_required
def userinfo_for_id(user_id:int):
    user: User = User.query.get(user_id)
    if not user:
        return r(404, '用户不存在')
    if request.method == 'PUT':
        user._set(dict(request.json))
    return r(data=user._get())


# ---------- application API ----------
@v1.route('/application/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def app_for_id(user_id:int, id:int):
    app: Application = Application.query.get(id)
    if not app:
        return r(404, 'APP不存在')
    if request.method == 'DELETE':
        app._del()
        return r(204)
    elif request.method == 'PUT':
        app._set(dict(request.json))
    return r(data=app._get())

@v1.route('/application', methods=['POST'])
@auth.login_required
def app(user_id:int):
    req = dict(request.json)
    app = Application()._set(req)
    return r(201, data=app._get())


# ---------- book API ----------
@v1.route('/book/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def book_for_id(user_id:int, id:int):
    book: Book = Book.query.get(id)
    if not book:
        return r(404, '账本不存在')
    if request.method == 'DELETE':
        book._del()
        return r(204)
    elif request.method == 'PUT':
        book._set(dict(request.json))
    return r(data=book._get())

@v1.route('/book', methods=['POST'])
@auth.login_required
def book(user_id:int):
    req = dict(request.json)
    book = Book()._set(req)
    user: User = User.query.get(user_id)
    user.books.append(book)
    UserBook.query.get((user.id, book.id)).permission = 7
    db.session.commit()

    return r(201)


# ---------- account API ----------
@v1.route('/account/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def account_for_id(user_id:int, id:int):
    account: Account = Account.query.get(id)
    if not account:
        return r(404, '资金账户不存在')
    if request.method == 'DELETE':
        account._del()
        return r(204)
    elif request.method == 'PUT':
        account._set(dict(request.json))
    return r(data=account._get())

@v1.route('/account', methods=['POST'])
@auth.login_required
def account(user_id:int):
    req = dict(request.json)
    #
    return r(201)


# ---------- category API ----------
@v1.route('/category/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def category_for_id(user_id:int, id:int):
    category: Category = Category.query.get(id)
    if not category:
        return r(404, '分类不存在')
    if request.method == 'DELETE':
        category._del()
        return r(204)
    elif request.method == 'PUT':
        category._set(dict(request.json))
    return r(data=category._get())

@v1.route('/category', methods=['POST'])
@auth.login_required
def category(user_id:int):
    req = dict(request.json)
    #
    return r(201)


# ---------- tag API ----------
@v1.route('/tag/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def tag_for_id(user_id:int, id:int):
    tag: Tag = Tag.query.get(id)
    if not tag:
        return r(404, '标签不存在')
    if request.method == 'DELETE':
        tag._del()
        return r(204)
    elif request.method == 'PUT':
        tag._set(dict(request.json))
    return r(data=tag._get())

@v1.route('/tag', methods=['POST'])
@auth.login_required
def tag(user_id:int):
    req = dict(request.json)
    #
    return r(201)


# ---------- tally API ----------
@v1.route('/tally/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def tally_for_id(user_id:int, id:int):
    tally: Tally = Tally.query.get(id)
    if not tally:
        return r(404, '记录不存在')
    if request.method == 'DELETE':
        tally._del()
        return r(204)
    elif request.method == 'PUT':
        tally._set(dict(request.json))
    return r(data=tally._get())

@v1.route('/tally', methods=['POST'])
@auth.login_required
def tally(user_id:int):
    req = dict(request.json)
    #
    return r(201)

@v1.route('/tallies', methods=['GET'])
@auth.login_required
def tallies(user_id:int):
    args = dict(request.args)
    tallies: list[Tally] = db.session.query(Tally).filter(Tally.book_id==args.get('book-id'), Tally.record_timestamp.between(args.get('start'), args.get('end'))).all()
    return r(data=[i._get() for i in tallies])



# ---------- list for filter API ----------
objs = {
    'users': (User, ()),
    'applications': (Application, ()),
    'books': (Book, ('id', 'name', 'remark', 'created')),
    'accounts': (Account, ()),
    'categories': (Category, ()),
    'tags': (Tag, ()),
}
@v1.route('/<obj_str>', methods=['GET'])
@auth.login_required
def filter_obj(user_id:int, obj_str:str):
    obj = objs.get(obj_str)
    if not obj:
        return r(404, '%s 未找到' % obj_str)
    args = dict(request.args)
    lists: list[any] = obj[0].query.filter_by(**args)
    return r(data=[i._get(obj[1]) for i in lists])
