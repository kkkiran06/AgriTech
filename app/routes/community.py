"""
KrishiMitra Community Q&A Forum Blueprint
Provides farmer-to-farmer knowledge sharing and verified expert replies.
Routes:
  GET  /community/           - List posts with category/tag filtering and search
  POST /community/new        - Create new question/post
  GET  /community/<post_id>  - View post and replies
  POST /community/<post_id>/reply - Add reply
  POST /community/<post_id>/upvote - Upvote post
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.database.db import get_db
from app.routes.helpers import login_required, get_current_farmer

community_bp = Blueprint('community', __name__)

CATEGORIES = [
    "Disease Help",
    "Pest Control",
    "Soil & Fertilizer",
    "Market Prices",
    "Weather",
    "Government Schemes",
    "General",
]

@community_bp.route('/')
def index():
    db = get_db()
    farmer = get_current_farmer()
    selected_cat = request.args.get('category', '').strip()
    tag = request.args.get('tag', '').strip()
    search = request.args.get('q', '').strip()

    query = """
        SELECT p.*, f.name as author_name, f.district as author_district,
               (SELECT COUNT(*) FROM community_replies r WHERE r.post_id = p.id) as reply_count
        FROM community_posts p
        JOIN farmers f ON p.farmer_id = f.id
        WHERE 1=1
    """
    params = []
    if selected_cat and selected_cat != 'All':
        query += " AND p.category = ?"
        params.append(selected_cat)
    if tag:
        query += " AND p.tags LIKE ?"
        params.append(f"%{tag}%")
    if search:
        query += " AND (p.title LIKE ? OR p.body LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY p.id DESC"
    posts = db.execute(query, tuple(params)).fetchall()

    return render_template(
        'community/index.html',
        posts=posts,
        categories=CATEGORIES,
        selected_category=selected_cat,
        selected_tag=tag,
        search_query=search,
        farmer=farmer
    )

@community_bp.route('/new', methods=['POST'])
@login_required
def create_post():
    farmer = get_current_farmer()
    title = request.form.get('title', '').strip()
    body = request.form.get('body', '').strip()
    category = request.form.get('category', 'General').strip()
    tags = request.form.get('tags', '').strip()

    if not title or len(title) < 5:
        flash("Title must be at least 5 characters.", "danger")
        return redirect(url_for('community.index'))
    if not body or len(body) < 10:
        flash("Question details must be at least 10 characters.", "danger")
        return redirect(url_for('community.index'))

    db = get_db()
    db.execute(
        """INSERT INTO community_posts (farmer_id, title, body, category, tags)
           VALUES (?, ?, ?, ?, ?)""",
        (farmer['id'], title, body, category, tags)
    )
    db.commit()
    flash("Your question has been posted to the Community Forum!", "success")
    return redirect(url_for('community.index'))

@community_bp.route('/<int:post_id>')
def detail(post_id):
    db = get_db()
    farmer = get_current_farmer()

    # Increment view count
    db.execute("UPDATE community_posts SET views = views + 1 WHERE id = ?", (post_id,))
    db.commit()

    post = db.execute(
        """SELECT p.*, f.name as author_name, f.district as author_district, f.state as author_state
           FROM community_posts p
           JOIN farmers f ON p.farmer_id = f.id
           WHERE p.id = ?""",
        (post_id,)
    ).fetchone()

    if not post:
        flash("Post not found.", "warning")
        return redirect(url_for('community.index'))

    replies = db.execute(
        """SELECT r.*, f.name as author_name, f.district as author_district
           FROM community_replies r
           JOIN farmers f ON r.farmer_id = f.id
           WHERE r.post_id = ?
           ORDER BY r.id ASC""",
        (post_id,)
    ).fetchall()

    return render_template('community/detail.html', post=post, replies=replies, farmer=farmer)

@community_bp.route('/<int:post_id>/reply', methods=['POST'])
@login_required
def add_reply(post_id):
    farmer = get_current_farmer()
    body = request.form.get('body', '').strip()
    if not body or len(body) < 3:
        flash("Reply cannot be empty.", "danger")
        return redirect(url_for('community.detail', post_id=post_id))

    # If the user is identified as an expert, flag reply
    is_expert = 1 if 'expert' in farmer.get('name', '').lower() else 0

    db = get_db()
    db.execute(
        """INSERT INTO community_replies (post_id, farmer_id, body, is_expert_verified)
           VALUES (?, ?, ?, ?)""",
        (post_id, farmer['id'], body, is_expert)
    )
    db.commit()
    flash("Your reply has been added.", "success")
    return redirect(url_for('community.detail', post_id=post_id))

@community_bp.route('/<int:post_id>/upvote', methods=['POST'])
@login_required
def upvote(post_id):
    db = get_db()
    db.execute("UPDATE community_posts SET upvotes = upvotes + 1 WHERE id = ?", (post_id,))
    db.commit()
    flash("Upvoted post!", "success")
    return redirect(url_for('community.detail', post_id=post_id))
