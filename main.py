from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy

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


class MostCommonDishes(db.Model):
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


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(main)


@main.route('/login')
def login():
    return render_template('login.html')


current_user_email = ''
current_user_name = ''
current_user_payment = 0


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

    user = User.query.filter_by(email=email).first()

    if user:
        flash('email address already exists.')
        return redirect(url_for('signup'))

    new_user = User(email=email, name = name, password=password)

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


@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@main.route('/menu_option')
@login_required
def menu_option():
    return render_template('menu_option.html')


@main.route("/view_menu")
@login_required
def view_menu():
    return render_template('view_option/view_menu.html')


@main.route("/view_account")
@login_required
def view_account():
    return render_template('view_option/view_account.html')


@main.route("/contact_us")
@login_required
def contact_us():
    return render_template('view_option/contact_us.html')


@main.route('/most_common_dishes', methods=['GET'])
def most_common_dishes():
    dishes = MostCommonDishes.query.order_by(MostCommonDishes.id).all()
    return render_template('view_option/view_menu/most_common_dishes.html', dishes=dishes)


@main.route('/most_common_dishes/<int:id>', methods=['GET', 'POST'])
def most_common_dishes_post(id):
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

    return redirect('/most_common_dishes')


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
        return render_template('most_common_dishes_manager.html', dishes=dishes)


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
        return render_template('most_common_dishes_update.html', dish=dish)


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
def manager():
    return render_template('manager.html')


class OrdersQuery:
    order_query = {}
    order_price = []


@main.route('/confirm_order')
def confirm_order():
    orders_orders = Order.query.filter_by(customer_id=current_user.id).all()
    orders = OrdersQuery()

    for order in orders_orders:
        if order.name not in orders.order_query.items():
            orders.order_query[order.name] = 0
            orders.order_price.append(order.price)
        orders.order_query[order.name] += 1
    
    final_order = []
    price_index = 0
    for key, value in orders.order_query.items():
        final_order.append((key, value, orders.order_price[price_index]))
        price_index += 1
        
    return render_template('confirm_order.html', orders=final_order)


if __name__ == '__main__':
    main.run(debug=True)
