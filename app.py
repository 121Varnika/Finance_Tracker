import os
import datetime
from datetime import timedelta
import click
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import create_tables, get_db_connection
import calendar

# --- App Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- All Routes ---

@app.route('/')
def dashboard():
    conn = get_db_connection()
    today = datetime.date.today()
    current_month_str = today.strftime("%Y-%m")
    monthly_income = conn.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income' AND strftime('%Y-%m', transaction_date) = ?", (current_month_str,)).fetchone()[0] or 0
    monthly_expense = conn.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense' AND strftime('%Y-%m', transaction_date) = ?", (current_month_str,)).fetchone()[0] or 0
    balance = (conn.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income'").fetchone()[0] or 0) - (conn.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense'").fetchone()[0] or 0)
    daily_expense = conn.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense' AND date(transaction_date) = ?", (today.strftime('%Y-%m-%d'),)).fetchone()[0] or 0
    start_of_week = today - timedelta(days=today.weekday())
    weekly_expense = conn.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense' AND date(transaction_date) >= ?", (start_of_week.strftime('%Y-%m-%d'),)).fetchone()[0] or 0
    wants_total = conn.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense' AND need_want = 'want' AND strftime('%Y-%m', transaction_date) = ?", (current_month_str,)).fetchone()[0] or 0
    needs_total = conn.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense' AND need_want = 'need' AND strftime('%Y-%m', transaction_date) = ?", (current_month_str,)).fetchone()[0] or 0
    health_score = 0
    notification = None
    if (wants_total + needs_total) > 0:
        wants_percentage = wants_total / (wants_total + needs_total)
        health_score = int((1 - wants_percentage) * 100)
        if wants_percentage > 0.5:
            notification = "Heads up! Spending on 'Wants' is higher than on 'Needs' this month."
    dashboard_goals = conn.execute('SELECT * FROM goals WHERE is_completed = 0 AND show_on_dashboard = 1 ORDER BY priority ASC').fetchall()
    expense_by_category = conn.execute("SELECT c.name, SUM(t.amount) as total FROM transactions t JOIN categories c ON t.category_id = c.id WHERE t.type = 'expense' AND strftime('%Y-%m', t.transaction_date) = ? GROUP BY c.name ORDER BY total DESC", (current_month_str,)).fetchall()
    doughnut_labels = [row['name'] for row in expense_by_category]
    doughnut_data = [row['total'] for row in expense_by_category]
    last_month_date = today.replace(day=1) - timedelta(days=1)
    last_month_str = last_month_date.strftime("%Y-%m")
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    line_labels = list(range(1, days_in_month + 1))
    this_month_expenses_raw = conn.execute("SELECT strftime('%d', transaction_date) as day, SUM(amount) as total FROM transactions WHERE type = 'expense' AND strftime('%Y-%m', transaction_date) = ? GROUP BY day", (current_month_str,)).fetchall()
    last_month_expenses_raw = conn.execute("SELECT strftime('%d', transaction_date) as day, SUM(amount) as total FROM transactions WHERE type = 'expense' AND strftime('%Y-%m', transaction_date) = ? GROUP BY day", (last_month_str,)).fetchall()
    this_month_data = [0] * days_in_month
    last_month_data = [0] * days_in_month
    for row in this_month_expenses_raw:
        this_month_data[int(row['day']) - 1] = row['total']
    for row in last_month_expenses_raw:
        if int(row['day']) <= days_in_month:
            last_month_data[int(row['day']) - 1] = row['total']
    conn.close()
    return render_template('dashboard.html', monthly_income=monthly_income, monthly_expense=monthly_expense, balance=balance, daily_expense=daily_expense, weekly_expense=weekly_expense, health_score=health_score, notification=notification, dashboard_goals=dashboard_goals, doughnut_labels=doughnut_labels, doughnut_data=doughnut_data, line_labels=line_labels, this_month_data=this_month_data, last_month_data=last_month_data)

@app.route('/check-pin', methods=['POST'])
def check_pin():
    submitted_pin = request.json.get('pin')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
    conn.close()
    if user and check_password_hash(user['pin_hash'], submitted_pin):
        conn = get_db_connection()
        balance = (conn.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income'").fetchone()[0] or 0) - (conn.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense'").fetchone()[0] or 0)
        conn.close()
        return jsonify({'success': True, 'balance': f'{balance:.2f}'})
    else:
        return jsonify({'success': False})

@app.route('/categories', methods=['GET', 'POST'])
def categories_page():
    conn = get_db_connection()
    if request.method == 'POST':
        transaction_date = request.form['date']
        description = request.form['description']
        amount = request.form['amount']
        category_id = request.form['category_id']
        need_want = request.form['need_want']
        payment_method = request.form['payment_method']
        conn.execute("INSERT INTO transactions (transaction_date, description, amount, type, category_id, need_want, payment_method) VALUES (?, ?, ?, 'expense', ?, ?, ?)",(transaction_date, description, amount, category_id, need_want, payment_method))
        conn.commit()
        conn.close()
        return redirect(url_for('transactions_page'))
    categories = conn.execute('SELECT * FROM categories ORDER BY name').fetchall()
    conn.close()
    return render_template('categories.html', categories=categories)

@app.route('/transactions')
def transactions_page():
    conn = get_db_connection()
    transactions = conn.execute("SELECT t.id, t.transaction_date, t.description, t.amount, t.need_want, t.payment_method, c.name as category_name FROM transactions t JOIN categories c ON t.category_id = c.id WHERE t.type = 'expense' ORDER BY t.transaction_date DESC").fetchall()
    conn.close()
    return render_template('transactions.html', transactions=transactions)

@app.route('/credited', methods=['GET', 'POST'])
def credited_page():
    conn = get_db_connection()
    if request.method == 'POST':
        transaction_date = request.form['date']
        description = request.form['description']
        amount = request.form['amount']
        payment_method = request.form['payment_method']
        conn.execute("INSERT INTO transactions (transaction_date, description, amount, type, payment_method) VALUES (?, ?, ?, 'income', ?)", (transaction_date, description, amount, payment_method))
        conn.commit()
        conn.close()
        return redirect(url_for('credited_page'))
    credited_transactions = conn.execute("SELECT id, transaction_date, description, amount, payment_method FROM transactions WHERE type = 'income' ORDER BY transaction_date DESC").fetchall()
    conn.close()
    return render_template('credited.html', transactions=credited_transactions)

@app.route('/delete-transaction/<int:id>', methods=['POST'])
def delete_transaction(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM transactions WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/manage-categories', methods=['GET', 'POST'])
def manage_categories_page():
    conn = get_db_connection()
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'category':
            name = request.form['name']
            budget_str = request.form.get('budget')
            budget = float(budget_str) if budget_str else 0.0
            is_recurring = 1 if 'is_recurring' in request.form else 0
            conn.execute('INSERT INTO categories (name, budget, is_recurring) VALUES (?, ?, ?)', (name, budget, is_recurring))
        elif form_type == 'goal':
            name = request.form['name']
            target_amount = request.form['target_amount']
            need_want = request.form.get('need_want')
            show_on_dashboard = 1 if 'show_on_dashboard' in request.form else 0
            image_filename = None
            if 'goal_image' in request.files:
                file = request.files['goal_image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_filename = filename
            conn.execute('INSERT INTO goals (name, target_amount, image_filename, need_want, show_on_dashboard) VALUES (?, ?, ?, ?, ?)', (name, target_amount, image_filename, need_want, show_on_dashboard))
        conn.commit()
        conn.close()
        return redirect(url_for('manage_categories_page'))
    categories = conn.execute('SELECT * FROM categories ORDER BY name').fetchall()
    goals = conn.execute('SELECT * FROM goals WHERE is_completed = 0 ORDER BY priority ASC, name ASC').fetchall()
    conn.close()
    return render_template('manage_categories.html', categories=categories, goals=goals)

@app.route('/update-goal/<int:id>', methods=['POST'])
def update_goal(id):
    conn = get_db_connection()
    if 'toggle_dashboard' in request.form:
        current_status = conn.execute('SELECT show_on_dashboard FROM goals WHERE id = ?', (id,)).fetchone()[0]
        new_status = 1 - current_status
        conn.execute('UPDATE goals SET show_on_dashboard = ? WHERE id = ?', (new_status, id))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_categories_page'))

@app.route('/update-goal-order', methods=['POST'])
def update_goal_order():
    goal_ids_order = request.json.get('order')
    conn = get_db_connection()
    for index, goal_id in enumerate(goal_ids_order):
        priority = index + 1
        conn.execute('UPDATE goals SET priority = ? WHERE id = ?', (priority, goal_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/delete-category/<int:id>', methods=['POST'])
def delete_category(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM categories WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Category deleted successfully.')
    return redirect(url_for('manage_categories_page'))

@app.route('/complete-goal/<int:id>', methods=['POST'])
def complete_goal(id):
    conn = get_db_connection()
    conn.execute('UPDATE goals SET is_completed = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Goal marked as complete! Great job!')
    return redirect(url_for('manage_categories_page'))

# --- CLI COMMANDS ---
@app.cli.command("init-db")
def init_db_command():
    create_tables()
    print("Initialized the database.")

@app.cli.command("set-pin")
@click.argument("pin")
def set_pin_command(pin):
    conn = get_db_connection()
    conn.execute("REPLACE INTO users (id, username, pin_hash) VALUES (?, ?, ?)", (1, 'default_user', generate_password_hash(pin)))
    conn.commit()
    conn.close()
    print(f"PIN for 'default_user' has been set.")

if __name__ == '__main__':
    app.run(debug=True)