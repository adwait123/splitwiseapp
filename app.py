from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///splitwise.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paid_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    split_between = db.Column(db.String(200), nullable=False)  # Comma-separated user IDs


# Routes
@app.route('/')
def home():
    users = User.query.all()
    expenses = Expense.query.all()
    return render_template('index.html', users=users, expenses=expenses)


@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form['name']
    user = User(name=name)
    db.session.add(user)
    db.session.commit()
    return jsonify({'status': 'User added', 'name': name})


@app.route('/add_expense', methods=['POST'])
def add_expense():
    description = request.form['description']
    amount = float(request.form['amount'])
    paid_by = int(request.form['paid_by'])
    split_between = request.form['split_between']

    expense = Expense(description=description, amount=amount, paid_by=paid_by, split_between=split_between)
    db.session.add(expense)
    db.session.commit()
    return jsonify({'status': 'Expense added', 'description': description})


@app.route('/balances', methods=['GET'])
def get_balances():
    users = User.query.all()
    balances = {user.id: 0 for user in users}

    expenses = Expense.query.all()
    for expense in expenses:
        amount_per_user = expense.amount / (len(expense.split_between.split(',')))
        for user_id in expense.split_between.split(','):
            if int(user_id) == expense.paid_by:
                balances[int(user_id)] += expense.amount - amount_per_user
            else:
                balances[int(user_id)] -= amount_per_user

    result = {User.query.get(user_id).name: balance for user_id, balance in balances.items()}
    return jsonify(result)


# Initialize DB
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
