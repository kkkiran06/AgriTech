"""
KrishiMitra Farm Financial Management & PMFBY Crop Insurance Blueprint
Routes:
  GET  /finance/                 - Financial Overview (P&L, Expenses, Income, Insurance Calculator)
  POST /finance/expenses/add     - Record farm expense
  POST /finance/expenses/delete/<id> - Delete expense
  POST /finance/income/add       - Record farm income
  POST /finance/income/delete/<id>   - Delete income
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.database.db import get_db
from app.routes.helpers import login_required, get_current_farmer

finance_bp = Blueprint('finance', __name__)

EXPENSE_CATEGORIES = [
    "Seed", "Fertilizer", "Pesticide", "Labour",
    "Machinery", "Irrigation", "Transport", "Other"
]

INCOME_SOURCES = [
    "Crop Sale", "Government Subsidy", "Other"
]

SEASONS = [
    "Kharif 2026", "Rabi 2026-27", "Kharif 2025", "Rabi 2025-26", "Zaid 2026"
]

@finance_bp.route('/')
@login_required
def index():
    farmer = get_current_farmer()
    db = get_db()

    # Expenses
    expenses = db.execute(
        "SELECT * FROM farm_expenses WHERE farmer_id = ? ORDER BY expense_date DESC",
        (farmer['id'],)
    ).fetchall()

    # Income
    income = db.execute(
        "SELECT * FROM farm_income WHERE farmer_id = ? ORDER BY income_date DESC",
        (farmer['id'],)
    ).fetchall()

    total_expense = sum(float(e['amount']) for e in expenses)
    total_income = sum(float(i['amount']) for i in income)
    net_profit = total_income - total_expense
    margin = (net_profit / total_income * 100) if total_income > 0 else 0.0

    # Expense breakdown by category
    cat_breakdown = {}
    for e in expenses:
        cat = e['category']
        cat_breakdown[cat] = cat_breakdown.get(cat, 0.0) + float(e['amount'])

    # Farms for dropdown
    farms = db.execute("SELECT id, name FROM farms WHERE farmer_id = ?", (farmer['id'],)).fetchall()

    return render_template(
        'finance/index.html',
        farmer=farmer,
        expenses=expenses,
        income=income,
        total_expense=total_expense,
        total_income=total_income,
        net_profit=net_profit,
        margin=margin,
        cat_breakdown=cat_breakdown,
        categories=EXPENSE_CATEGORIES,
        sources=INCOME_SOURCES,
        seasons=SEASONS,
        farms=farms,
        today_date=datetime.now().strftime('%Y-%m-%d')
    )

@finance_bp.route('/expenses/add', methods=['POST'])
@login_required
def add_expense():
    farmer = get_current_farmer()
    category = request.form.get('category', 'Other').strip()
    description = request.form.get('description', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    expense_date = request.form.get('expense_date', datetime.now().strftime('%Y-%m-%d')).strip()
    season = request.form.get('season', 'Kharif 2026').strip()
    farm_id = request.form.get('farm_id') or None

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash("Expense amount must be greater than zero.", "danger")
            return redirect(url_for('finance.index'))
    except ValueError:
        flash("Invalid expense amount.", "danger")
        return redirect(url_for('finance.index'))

    if not description:
        description = f"{category} purchase"

    db = get_db()
    db.execute(
        """INSERT INTO farm_expenses (farmer_id, farm_id, category, description, amount, expense_date, season)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (farmer['id'], farm_id, category, description, amount, expense_date, season)
    )
    db.commit()
    flash(f"Expense of ₹{amount:,.0f} recorded under '{category}'.", "success")
    return redirect(url_for('finance.index'))

@finance_bp.route('/expenses/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    farmer = get_current_farmer()
    db = get_db()
    cur = db.execute("DELETE FROM farm_expenses WHERE id = ? AND farmer_id = ?", (expense_id, farmer['id']))
    db.commit()
    if cur.rowcount > 0:
        flash("Expense record deleted.", "info")
    else:
        flash("Record not found or unauthorized.", "danger")
    return redirect(url_for('finance.index'))

@finance_bp.route('/income/add', methods=['POST'])
@login_required
def add_income():
    farmer = get_current_farmer()
    source = request.form.get('source', 'Crop Sale').strip()
    description = request.form.get('description', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    income_date = request.form.get('income_date', datetime.now().strftime('%Y-%m-%d')).strip()
    season = request.form.get('season', 'Kharif 2026').strip()
    farm_id = request.form.get('farm_id') or None
    qty_str = request.form.get('quantity_quintal', '').strip()
    rate_str = request.form.get('price_per_quintal', '').strip()

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash("Income amount must be greater than zero.", "danger")
            return redirect(url_for('finance.index'))
        qty = float(qty_str) if qty_str else None
        rate = float(rate_str) if rate_str else None
    except ValueError:
        flash("Invalid income numbers.", "danger")
        return redirect(url_for('finance.index'))

    if not description:
        description = f"{source} receipt"

    db = get_db()
    db.execute(
        """INSERT INTO farm_income 
           (farmer_id, farm_id, source, description, amount, income_date, season, quantity_quintal, price_per_quintal)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (farmer['id'], farm_id, source, description, amount, income_date, season, qty, rate)
    )
    db.commit()
    flash(f"Income of ₹{amount:,.0f} recorded successfully.", "success")
    return redirect(url_for('finance.index'))

@finance_bp.route('/income/delete/<int:income_id>', methods=['POST'])
@login_required
def delete_income(income_id):
    farmer = get_current_farmer()
    db = get_db()
    cur = db.execute("DELETE FROM farm_income WHERE id = ? AND farmer_id = ?", (income_id, farmer['id']))
    db.commit()
    if cur.rowcount > 0:
        flash("Income record deleted.", "info")
    else:
        flash("Record not found or unauthorized.", "danger")
    return redirect(url_for('finance.index'))

@finance_bp.route('/insurance/calculate', methods=['POST'])
def calculate_insurance():
    from flask import jsonify
    data = request.get_json(silent=True) or request.form
    crop = data.get('crop_name', 'Paddy')
    area = float(data.get('area_acres', 1.0))
    sum_insured_per_acre = float(data.get('sum_insured_per_acre', 35000))
    season = data.get('season', 'Kharif')

    # PMFBY standard rates: Kharif Food/Oilseeds: 2.0%, Rabi Food/Oilseeds: 1.5%, Commercial/Horticultural: 5.0%
    if 'Kharif' in season:
        pct = 2.0
    elif 'Rabi' in season:
        pct = 1.5
    else:
        pct = 5.0

    total_sum_insured = area * sum_insured_per_acre
    farmer_premium = (total_sum_insured * pct) / 100.0
    govt_subsidy = (total_sum_insured * (12.0 - pct)) / 100.0  # Approx actuarial rate ~ 12%

    return jsonify({
        'crop_name': crop,
        'area_acres': area,
        'season': season,
        'sum_insured_per_acre': sum_insured_per_acre,
        'total_sum_insured': total_sum_insured,
        'farmer_share_pct': pct,
        'farmer_premium': farmer_premium,
        'govt_subsidy': max(0, govt_subsidy),
        'scheme': 'Pradhan Mantri Fasal Bima Yojana (PMFBY)'
    })
