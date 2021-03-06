from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


main = Flask(__name__)

main.config['SECRET_KEY'] = 'my_secret_key'
main.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(main)
db.init_app(main)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    number_of_order = db.Column(db.Integer, default=0)
    total_price = db.Column(db.Integer, default=0)
    prepare_status = db.Column(db.Integer, default=0)


class MostCommonDishes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer)

    def __repr__(self):
        return '<Dish %r>' % self.id


class NewDishes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer)

    def __repr__(self):
        return '<Dish %r>' % self.id


class Combo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer)

    def __repr__(self):
        return '<Dish %r>' % self.id


class Appetizers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer)

    def __repr__(self):
        return '<Dish %r>' % self.id


class Soup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer)

    def __repr__(self):
        return '<Dish %r>' % self.id


class Salad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer)

    def __repr__(self):
        return '<Dish %r>' % self.id


class Dessert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer)

    def __repr__(self):
        return '<Dish %r>' % self.id


class Drinks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer)

    def __repr__(self):
        return '<Dish %r>' % self.id


class MainDishes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer)

    def __repr__(self):
        return '<Dish %r>' % self.id


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer)


class OrderHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=False)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(main)


@main.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        if current_user.id == 1:
            return render_template('manager.html')
        return redirect('menu_option')
        
    return render_template('index.html')


@main.route('/login')
def login():
    return render_template('login.html')


@main.route('/qr_code')
def qr_code():
    return render_template('qr_code.html')


@main.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or password != user.password:
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))

    login_user(user, remember=True)

    if user.id == 1:
        return redirect('manager')
    return redirect(url_for('menu_option'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@main.route('/signup')
def signup():
    return render_template('signup.html')


@main.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('email address already exists.')
        return redirect(url_for('signup'))

    if password != confirm_password:
        flash('Password does not match')
        return redirect(url_for('signup'))

    new_user = User(email=email, name=name, password=password)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/order_history')
@login_required
def order_history():
    orders_orders = OrderHistory.query.filter_by(customer_id=current_user.id).all()
    order_histories = []
    if len(orders_orders) > 0:
        for order_meal_index in range(orders_orders[-1].order_id + 1):
            orders = []
            order_meal = [x for x in orders_orders if x.order_id == order_meal_index]
            for order in order_meal:
                flag = False
                for index_i in range(len(orders)):
                    if orders[index_i][0] == order.name:
                        orders[index_i][1] += 1
                        flag = True
                if not flag:
                    orders.append([order.name, 1, order.price, order.total_price, order.date_created.date()])
            order_histories.append(orders)

    return render_template('view_option/view_account/order_history.html', order_histories=order_histories)


@main.route('/menu_option')
@login_required
def menu_option():
    return render_template('menu_option.html')

@main.route('/shopping_cart')
@login_required
def shopping_cart():
    return render_template('cart.html')


@main.route("/view_menu")
@login_required
def view_menu():
    most_common_dishes = MostCommonDishes.query.order_by(MostCommonDishes.id).all()
    appetizers = Appetizers.query.order_by(Appetizers.id).all()
    new_dishes = NewDishes.query.order_by(NewDishes.id).all()
    combo = Combo.query.order_by(Combo.id).all()
    soup = Soup.query.order_by(Soup.id).all()
    salad = Salad.query.order_by(Salad.id).all()
    dessert = Dessert.query.order_by(Dessert.id).all()
    drinks = Drinks.query.order_by(Drinks.id).all()
    main_dishes = MainDishes.query.order_by(MainDishes.id).all()
    orders_orders = Order.query.filter_by(customer_id=current_user.id).all()

    orders = []
    for order in orders_orders:
        flag = False
        for index_i in range(len(orders)):
            if orders[index_i][0] == order.name:
                orders[index_i][1] += 1
                flag = True
        if not flag:
            orders.append([order.name, 1, order.price])
    return render_template('view_option/view_menu.html', most_common_dishes=most_common_dishes, combo=combo, orders=orders,
    new_dishes=new_dishes, soup=soup, salad=salad, dessert=dessert, drinks=drinks, main_dishes=main_dishes, appetizers=appetizers)


@main.route("/view_account")
@login_required
def view_account():
    return render_template('view_option/view_account.html')


@main.route("/contact_us")
def contact_us():
    return render_template('view_option/contact_us.html')


@main.route('/most_common_dishes', methods=['GET'])
def most_common_dishes():
    dishes = MostCommonDishes.query.order_by(MostCommonDishes.id).all()
    return render_template('view_option/view_menu/most_common_dishes.html', dishes=dishes)


@main.route('/most_common_dishes/<int:id>', methods=['GET', 'POST'])
def most_common_dishes_post(id):
    if current_user.prepare_status > 0:
        flash('Your current order is on the way')
        return redirect(url_for('most_common_dishes'))
    current = current_user.name
    dish = MostCommonDishes.query.get_or_404(id)
    current_user_id = current_user.id
    current_user_object = User.query.get_or_404(current_user_id)
    current_user_object.number_of_order += 1
    current_user_object.total_price += dish.price
    order_name = dish.name
    order_price = dish.price
    new_order = Order(customer_id=current_user_id, name=order_name, price=order_price)

    try:
        db.session.add(new_order)
        db.session.commit()
    except:
        return 'There was an issue adding your dish'

    return redirect('/view_menu')


@main.route('/most_common_dishes_manager', methods=['POST', 'GET'])
def most_common_dishes_manager():
    if request.method == 'POST':
        input_name = request.form['name']
        input_price = request.form['price']
        new_dish = MostCommonDishes(name=input_name, price=input_price)

        try:
            db.session.add(new_dish)
            db.session.commit()
            return redirect('/most_common_dishes_manager')
        except:
            return 'There was an issue adding your dish'

    else:
        dishes = MostCommonDishes.query.order_by(MostCommonDishes.id).all()
        return render_template('menu_manager/most_common_dishes_manager.html', dishes=dishes)


@main.route('/most_common_dishes_update/<int:id>', methods=['GET', 'POST'])
def most_common_dishes_update(id):
    dish = MostCommonDishes.query.get_or_404(id)

    if request.method == 'POST':
        dish.name = request.form['name']
        dish.price = request.form['price']

        try:
            db.session.commit()
            return redirect('/most_common_dishes_manager')
        except:
            return 'There was an issue updating your dish'

    else:
        return render_template('menu_manager/most_common_dishes_update.html', dish=dish)


@main.route('/most_common_dishes_delete/<int:id>')
def most_common_dishes_delete(id):
    task_to_delete = MostCommonDishes.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/most_common_dishes_manager')
    except:
        return 'There was a problem deleting that task'


@main.route('/manager')
@login_required
def manager():
    if current_user.id != 1:
        flash('Please login with the manager account')
        return redirect('menu_option')
    return render_template('manager.html')


@main.route('/confirm_order')
@login_required
def confirm_order():
    orders_orders = Order.query.filter_by(customer_id=current_user.id).all()

    orders = []
    for order in orders_orders:
        flag = False
        for index_i in range(len(orders)):
            if orders[index_i][0] == order.name:
                orders[index_i][1] += 1
                flag = True
        if not flag:
            orders.append([order.name, 1, order.price])

    return render_template('confirm_order.html', orders=orders)


@main.route('/confirm_order', methods=['POST'])
@login_required
def confirm_order_post():
    current_user_status = User.query.filter_by(id=current_user.id).first()

    if current_user_status.number_of_order <= 0:
        flash('Please choose your order')
        return redirect('confirm_order')
    current_user_status.prepare_status = 1
    db.session.commit()
    return redirect('order_status')


@main.route('/order_status')
@login_required
def order_status():
    orders_orders = Order.query.filter_by(customer_id=current_user.id).all()

    orders = []
    for order in orders_orders:
        flag = False
        for index_i in range(len(orders)):
            if orders[index_i][0] == order.name:
                orders[index_i][1] += 1
                flag = True
        if not flag:
            orders.append([order.name, 1, order.price])

    return render_template('order_status.html', orders=orders)


@main.route('/order_status', methods=['POST'])
@login_required
def order_status_post():
    payment_method = request.form.get('payment')
    payment_method = str(payment_method)

    customer = User.query.filter_by(id=current_user.id).first()
    current_total_price = current_user.total_price
    customer.prepare_status = 0
    customer.number_of_order = 0
    customer.total_price = 0

    orders = Order.query.filter_by(customer_id=current_user.id).all()
    order_id_all = OrderHistory.query.filter_by(customer_id=current_user.id).all()
    if len(order_id_all) == 0:
        current_order_id = 0
    else:
        current_order_id = int(order_id_all[-1] .order_id) + 1
    for order in orders:
        db.session.add(OrderHistory(customer_id=current_user.id, order_id=current_order_id,name=order.name,
                                    price=order.price, total_price=current_total_price, payment_method=payment_method))
        db.session.delete(order)

    db.session.commit()
    return redirect(url_for('rating'))


@main.route('/rating')
@login_required
def rating():
    return render_template('rating.html')


@main.route('/customer_manager')
@login_required
def customer_manager():
    customers_pending = User.query.filter_by(prepare_status=1).all()
    customers_preparing = User.query.filter_by(prepare_status=2).all()
    customers_delivering = User.query.filter_by(prepare_status=3).all()
    customers_delivered = User.query.filter_by(prepare_status=4).all()
    return render_template('customer_manager.html', pending=customers_pending,
                           preparing=customers_preparing, delivering=customers_delivering, delivered=customers_delivered)


@main.route('/change_password')
@login_required
def change_password():
    return render_template('view_option/view_account/change_password.html')


@main.route('/change_password', methods=['POST'])
@login_required
def change_password_post():
    current_password = request.form['current_password']
    if current_user.password != current_password:
        flash('Your current password is not correct, please try again')
        return redirect('/change_password')
    new_password = request.form['new_password']
    confirm_new_password = request.form['confirm_new_password']

    if new_password != confirm_new_password:
        flash('Confirm password do not match, please try again')
        return redirect('change_password')
    current_user.password = current_password
    flash('Password changed')
    return redirect('/change_password')


@main.route('/order_manager')
@login_required
def order_manager():
    orders_orders = OrderHistory.query.order_by(OrderHistory.date_created).all()
    order_histories = []
    if len(orders_orders) > 0:
        for order_meal_index in range(orders_orders[-1].order_id + 1):
            orders = []
            order_meal = [x for x in orders_orders if x.order_id == order_meal_index]
            for order in order_meal:
                flag = False
                for index_i in range(len(orders)):
                    if orders[index_i][0] == order.name:
                        orders[index_i][1] += 1
                        flag = True
                if not flag:
                    orders.append([order.name, 1, order.price, order.total_price, order.date_created,
                                   User.query.filter_by(id=order.customer_id).first().name, order.payment_method])
            order_histories.append(orders)

    return render_template('order_manager.html', order_histories=order_histories)


@main.route('/customer_manager_accept_order/<int:id>', methods=['POST', 'GET'])
def customer_manager_accept_order(id):
    customer = User.query.filter_by(id=id).first()
    customer.prepare_status = 2
    db.session.commit()
    return redirect(url_for('customer_manager'))


@main.route('/customer_manager_deliver_order/<int:id>', methods=['POST', 'GET'])
def customer_manager_deliver_order(id):
    customer = User.query.filter_by(id=id).first()
    customer.prepare_status = 3
    db.session.commit()
    return redirect(url_for('customer_manager'))


@main.route('/customer_manager_delivering_order/<int:id>', methods=['POST', 'GET'])
def customer_manager_delivering_order(id):
    customer = User.query.filter_by(id=id).first()
    customer.prepare_status = 4
    db.session.commit()
    return redirect(url_for('customer_manager'))


@main.route('/customer_manager_delete_order/<int:id>', methods=['POST', 'GET'])
def customer_manager_delete_order(id):
    customer = User.query.filter_by(id=id).first()
    customer.prepare_status = 0
    customer.number_of_order = 0
    customer.total_price = 0

    orders = Order.query.filter_by(customer_id=id).all()
    for order in orders:
        db.session.delete(order)

    db.session.commit()
    if (current_user.id != 1):
        return redirect(url_for('view_menu'))
    return redirect(url_for('customer_manager'))


@main.route('/new_dishes', methods=['GET'])
def new_dishes():
    dishes = NewDishes.query.order_by(NewDishes.id).all()
    return render_template('view_option/view_menu/new_dishes.html', dishes=dishes)


@main.route('/new_dishes/<int:id>', methods=['GET', 'POST'])
def new_dishes_post(id):
    if current_user.prepare_status > 0:
        flash('Your current order is on the way')
        return redirect(url_for('new_dishes'))
    dish = NewDishes.query.get_or_404(id)
    current_user_id = current_user.id
    current_user_object = User.query.get_or_404(current_user_id)
    current_user_object.number_of_order += 1
    current_user_object.total_price += dish.price
    order_name = dish.name
    order_price = dish.price
    new_order = Order(customer_id=current_user_id, name=order_name, price=order_price)

    try:
        db.session.add(new_order)
        db.session.commit()
    except:
        return 'There was an issue adding your dish'

    return redirect('/view_menu')


@main.route('/new_dishes_manager', methods=['POST', 'GET'])
def new_dishes_manager():
    if request.method == 'POST':
        input_name = request.form['name']
        input_price = request.form['price']
        new_dish = NewDishes(name=input_name, price=input_price)

        try:
            db.session.add(new_dish)
            db.session.commit()
            return redirect('/new_dishes_manager')
        except:
            return 'There was an issue adding your dish'

    else:
        dishes = NewDishes.query.order_by(NewDishes.id).all()
        return render_template('menu_manager/new_dishes_manager.html', dishes=dishes)


@main.route('/new_dishes_update/<int:id>', methods=['GET', 'POST'])
def new_dishes_update(id):
    dish = NewDishes.query.get_or_404(id)

    if request.method == 'POST':
        dish.name = request.form['name']
        dish.price = request.form['price']

        try:
            db.session.commit()
            return redirect('/new_dishes_manager')
        except:
            return 'There was an issue updating your dish'

    else:
        return render_template('menu_manager/new_dishes_update.html', dish=dish)


@main.route('/new_dishes_delete/<int:id>')
def new_dishes_delete(id):
    task_to_delete = NewDishes.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/new_dishes_manager')
    except:
        return 'There was a problem deleting that task'


@main.route('/combo', methods=['GET'])
def combo():
    dishes = Combo.query.order_by(Combo.id).all()
    return render_template('view_option/view_menu/combo.html', dishes=dishes)


@main.route('/combo/<int:id>', methods=['GET', 'POST'])
def combo_post(id):
    if current_user.prepare_status > 0:
        flash('Your current order is on the way')
        return redirect(url_for('combo'))
    dish = Combo.query.get_or_404(id)
    current_user_id = current_user.id
    current_user_object = User.query.get_or_404(current_user_id)
    current_user_object.number_of_order += 1
    current_user_object.total_price += dish.price
    order_name = dish.name
    order_price = dish.price
    new_order = Order(customer_id=current_user_id, name=order_name, price=order_price)

    try:
        db.session.add(new_order)
        db.session.commit()
    except:
        return 'There was an issue adding your dish'

    return redirect('/view_menu')


@main.route('/combo_manager', methods=['POST', 'GET'])
def combo_manager():
    if request.method == 'POST':
        input_name = request.form['name']
        input_price = request.form['price']
        new_dish = Combo(name=input_name, price=input_price)

        try:
            db.session.add(new_dish)
            db.session.commit()
            return redirect('/combo_manager')
        except:
            return 'There was an issue adding your dish'

    else:
        dishes = Combo.query.order_by(Combo.id).all()
        return render_template('menu_manager/combo_manager.html', dishes=dishes)


@main.route('/combo_update/<int:id>', methods=['GET', 'POST'])
def combo_update(id):
    dish = Combo.query.get_or_404(id)

    if request.method == 'POST':
        dish.name = request.form['name']
        dish.price = request.form['price']

        try:
            db.session.commit()
            return redirect('/combo_manager')
        except:
            return 'There was an issue updating your dish'

    else:
        return render_template('menu_manager/combo_update.html', dish=dish)


@main.route('/combo_delete/<int:id>')
def combo_delete(id):
    task_to_delete = Combo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/combo_manager')
    except:
        return 'There was a problem deleting that task'


@main.route('/appetizers', methods=['GET'])
def appetizers():
    dishes = Appetizers.query.order_by(Appetizers.id).all()
    return render_template('view_option/view_menu/appetizers.html', dishes=dishes)


@main.route('/appetizers/<int:id>', methods=['GET', 'POST'])
def appetizers_post(id):
    if current_user.prepare_status > 0:
        flash('Your current order is on the way')
        return redirect(url_for('appetizers'))
    dish = Appetizers.query.get_or_404(id)
    current_user_id = current_user.id
    current_user_object = User.query.get_or_404(current_user_id)
    current_user_object.number_of_order += 1
    current_user_object.total_price += dish.price
    order_name = dish.name
    order_price = dish.price
    new_order = Order(customer_id=current_user_id, name=order_name, price=order_price)

    try:
        db.session.add(new_order)
        db.session.commit()
    except:
        return 'There was an issue adding your dish'

    return redirect('/view_menu')


@main.route('/appetizers_manager', methods=['POST', 'GET'])
def appetizers_manager():
    if request.method == 'POST':
        input_name = request.form['name']
        input_price = request.form['price']
        new_dish = Appetizers(name=input_name, price=input_price)

        try:
            db.session.add(new_dish)
            db.session.commit()
            return redirect('/appetizers_manager')
        except:
            return 'There was an issue adding your dish'

    else:
        dishes = Appetizers.query.order_by(Appetizers.id).all()
        return render_template('menu_manager/appetizers_manager.html', dishes=dishes)


@main.route('/appetizers_update/<int:id>', methods=['GET', 'POST'])
def appetizers_update(id):
    dish = Appetizers.query.get_or_404(id)

    if request.method == 'POST':
        dish.name = request.form['name']
        dish.price = request.form['price']

        try:
            db.session.commit()
            return redirect('/appetizers_manager')
        except:
            return 'There was an issue updating your dish'

    else:
        return render_template('menu_manager/appetizers_update.html', dish=dish)


@main.route('/appetizers_delete/<int:id>')
def appetizers_delete(id):
    task_to_delete = Appetizers.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/appetizers_manager')
    except:
        return 'There was a problem deleting that task'


@main.route('/soup', methods=['GET'])
def soup():
    dishes = Soup.query.order_by(Soup.id).all()
    return render_template('view_option/view_menu/soup.html', dishes=dishes)


@main.route('/soup/<int:id>', methods=['GET', 'POST'])
def soup_post(id):
    if current_user.prepare_status > 0:
        flash('Your current order is on the way')
        return redirect(url_for('soup'))
    dish = Soup.query.get_or_404(id)
    current_user_id = current_user.id
    current_user_object = User.query.get_or_404(current_user_id)
    current_user_object.number_of_order += 1
    current_user_object.total_price += dish.price
    order_name = dish.name
    order_price = dish.price
    new_order = Order(customer_id=current_user_id, name=order_name, price=order_price)

    try:
        db.session.add(new_order)
        db.session.commit()
    except:
        return 'There was an issue adding your dish'

    return redirect('/view_menu')


@main.route('/soup_manager', methods=['POST', 'GET'])
def soup_manager():
    if request.method == 'POST':
        input_name = request.form['name']
        input_price = request.form['price']
        new_dish = Soup(name=input_name, price=input_price)

        try:
            db.session.add(new_dish)
            db.session.commit()
            return redirect('/soup_manager')
        except:
            return 'There was an issue adding your dish'

    else:
        dishes =Soup.query.order_by(Soup.id).all()
        return render_template('menu_manager/soup_manager.html', dishes=dishes)


@main.route('/soup_update/<int:id>', methods=['GET', 'POST'])
def soup_update(id):
    dish = Soup.query.get_or_404(id)

    if request.method == 'POST':
        dish.name = request.form['name']
        dish.price = request.form['price']

        try:
            db.session.commit()
            return redirect('/soup_manager')
        except:
            return 'There was an issue updating your dish'

    else:
        return render_template('menu_manager/soup_update.html', dish=dish)


@main.route('/soup_delete/<int:id>')
def soup_delete(id):
    task_to_delete = Soup.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/soup_manager')
    except:
        return 'There was a problem deleting that task'


@main.route('/salad', methods=['GET'])
def salad():
    dishes = Salad.query.order_by(Salad.id).all()
    return render_template('view_option/view_menu/salad.html', dishes=dishes)


@main.route('/salad/<int:id>', methods=['GET', 'POST'])
def salad_post(id):
    if current_user.prepare_status > 0:
        flash('Your current order is on the way')
        return redirect(url_for('salad'))
    dish = Salad.query.get_or_404(id)
    current_user_id = current_user.id
    current_user_object = User.query.get_or_404(current_user_id)
    current_user_object.number_of_order += 1
    current_user_object.total_price += dish.price
    order_name = dish.name
    order_price = dish.price
    new_order = Order(customer_id=current_user_id, name=order_name, price=order_price)

    try:
        db.session.add(new_order)
        db.session.commit()
    except:
        return 'There was an issue adding your dish'

    return redirect('/view_menu')


@main.route('/salad_manager', methods=['POST', 'GET'])
def salad_manager():
    if request.method == 'POST':
        input_name = request.form['name']
        input_price = request.form['price']
        new_dish = Salad(name=input_name, price=input_price)

        try:
            db.session.add(new_dish)
            db.session.commit()
            return redirect('/salad_manager')
        except:
            return 'There was an issue adding your dish'

    else:
        dishes = Salad.query.order_by(Salad.id).all()
        return render_template('menu_manager/salad_manager.html', dishes=dishes)


@main.route('/salad_update/<int:id>', methods=['GET', 'POST'])
def salad_update(id):
    dish = Salad.query.get_or_404(id)

    if request.method == 'POST':
        dish.name = request.form['name']
        dish.price = request.form['price']

        try:
            db.session.commit()
            return redirect('/salad_manager')
        except:
            return 'There was an issue updating your dish'

    else:
        return render_template('menu_manager/salad_update.html', dish=dish)


@main.route('/salad_delete/<int:id>')
def salad_delete(id):
    task_to_delete =Salad.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/salad_manager')
    except:
        return 'There was a problem deleting that task'


@main.route('/dessert', methods=['GET'])
def dessert():
    dishes = Dessert.query.order_by(Dessert.id).all()
    return render_template('view_option/view_menu/dessert.html', dishes=dishes)


@main.route('/dessert/<int:id>', methods=['GET', 'POST'])
def dessert_post(id):
    if current_user.prepare_status > 0:
        flash('Your current order is on the way')
        return redirect(url_for('dessert'))
    dish = Dessert.query.get_or_404(id)
    current_user_id = current_user.id
    current_user_object = User.query.get_or_404(current_user_id)
    current_user_object.number_of_order += 1
    current_user_object.total_price += dish.price
    order_name = dish.name
    order_price = dish.price
    new_order = Order(customer_id=current_user_id, name=order_name, price=order_price)

    try:
        db.session.add(new_order)
        db.session.commit()
    except:
        return 'There was an issue adding your dish'

    return redirect('/view_menu')


@main.route('/dessert_manager', methods=['POST', 'GET'])
def dessert_manager():
    if request.method == 'POST':
        input_name = request.form['name']
        input_price = request.form['price']
        new_dish = Dessert(name=input_name, price=input_price)

        try:
            db.session.add(new_dish)
            db.session.commit()
            return redirect('/dessert_manager')
        except:
            return 'There was an issue adding your dish'

    else:
        dishes = Dessert.query.order_by(Dessert.id).all()
        return render_template('menu_manager/dessert_manager.html', dishes=dishes)


@main.route('/dessert_update/<int:id>', methods=['GET', 'POST'])
def dessert_update(id):
    dish = Dessert.query.get_or_404(id)

    if request.method == 'POST':
        dish.name = request.form['name']
        dish.price = request.form['price']

        try:
            db.session.commit()
            return redirect('/dessert_manager')
        except:
            return 'There was an issue updating your dish'

    else:
        return render_template('menu_manager/dessert_update.html', dish=dish)


@main.route('/dessert_delete/<int:id>')
def dessert_delete(id):
    task_to_delete = Dessert.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/dessert_manager')
    except:
        return 'There was a problem deleting that task'


@main.route('/drinks', methods=['GET'])
def drinks():
    dishes = Drinks.query.order_by(Drinks.id).all()
    return render_template('view_option/view_menu/drinks.html', dishes=dishes)


@main.route('/drinks/<int:id>', methods=['GET', 'POST'])
def drinks_post(id):
    if current_user.prepare_status > 0:
        flash('Your current order is on the way')
        return redirect(url_for('drinks'))
    dish = Drinks.query.get_or_404(id)
    current_user_id = current_user.id
    current_user_object = User.query.get_or_404(current_user_id)
    current_user_object.number_of_order += 1
    current_user_object.total_price += dish.price
    order_name = dish.name
    order_price = dish.price
    new_order = Order(customer_id=current_user_id, name=order_name, price=order_price)

    try:
        db.session.add(new_order)
        db.session.commit()
    except:
        return 'There was an issue adding your dish'

    return redirect('/view_menu')


@main.route('/drinks_manager', methods=['POST', 'GET'])
def drinks_manager():
    if request.method == 'POST':
        input_name = request.form['name']
        input_price = request.form['price']
        new_dish = Drinks(name=input_name, price=input_price)

        try:
            db.session.add(new_dish)
            db.session.commit()
            return redirect('/drinks_manager')
        except:
            return 'There was an issue adding your dish'

    else:
        dishes = Drinks.query.order_by(Drinks.id).all()
        return render_template('menu_manager/drinks_manager.html', dishes=dishes)


@main.route('/drinks_update/<int:id>', methods=['GET', 'POST'])
def drinks_update(id):
    dish = Drinks.query.get_or_404(id)

    if request.method == 'POST':
        dish.name = request.form['name']
        dish.price = request.form['price']

        try:
            db.session.commit()
            return redirect('/drinks_manager')
        except:
            return 'There was an issue updating your dish'

    else:
        return render_template('menu_manager/drinks_update.html', dish=dish)


@main.route('/drinks_delete/<int:id>')
def drinks_delete(id):
    task_to_delete = Drinks.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/drinks_manager')
    except:
        return 'There was a problem deleting that task'


@main.route('/main_dishes', methods=['GET'])
def main_dishes():
    dishes = MainDishes.query.order_by(MainDishes.id).all()
    return render_template('view_option/view_menu/main_dishes.html', dishes=dishes)


@main.route('/main_dishes/<int:id>', methods=['GET', 'POST'])
def main_dishes_post(id):
    if current_user.prepare_status > 0:
        flash('Your current order is on the way')
        return redirect(url_for('main_dishes'))
    dish = MainDishes.query.get_or_404(id)
    current_user_id = current_user.id
    current_user_object = User.query.get_or_404(current_user_id)
    current_user_object.number_of_order += 1
    current_user_object.total_price += dish.price
    order_name = dish.name
    order_price = dish.price
    new_order = Order(customer_id=current_user_id, name=order_name, price=order_price)

    try:
        db.session.add(new_order)
        db.session.commit()
    except:
        return 'There was an issue adding your dish'

    return redirect('/view_menu')


@main.route('/main_dishes_manager', methods=['POST', 'GET'])
def main_dishes_manager():
    if request.method == 'POST':
        input_name = request.form['name']
        input_price = request.form['price']
        new_dish = MainDishes(name=input_name, price=input_price)

        try:
            db.session.add(new_dish)
            db.session.commit()
            return redirect('/main_dishes_manager')
        except:
            return 'There was an issue adding your dish'

    else:
        dishes = MainDishes.query.order_by(MainDishes.id).all()
        return render_template('menu_manager/main_dishes_manager.html', dishes=dishes)


@main.route('/main_dishes_update/<int:id>', methods=['GET', 'POST'])
def main_dishes_update(id):
    dish = MainDishes.query.get_or_404(id)

    if request.method == 'POST':
        dish.name = request.form['name']
        dish.price = request.form['price']

        try:
            db.session.commit()
            return redirect('/main_dishes_manager')
        except:
            return 'There was an issue updating your dish'

    else:
        return render_template('menu_manager/main_dishes_update.html', dish=dish)


@main.route('/main_dishes_delete/<int:id>')
def main_dishes_delete(id):
    task_to_delete = MainDishes.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/main_dishes_manager')
    except:
        return 'There was a problem deleting that task'


if __name__ == '__main__':
    main.run(debug=True)
