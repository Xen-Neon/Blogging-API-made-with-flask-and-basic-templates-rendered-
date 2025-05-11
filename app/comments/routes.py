
from flask import Blueprint, request, jsonify, abort, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import current_user, login_required
from app import db
from app.models import Comment, Post

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/<int:post_id>/add', methods=['GET', 'POST'])
@login_required
@jwt_required(optional=True)
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        data = request.form if request.form else request.get_json()
        content = data.get('content')
        parent_id = data.get('parent_id')
        if not content:
            flash('Content is required')
            return render_template('add_comment.html', post=post)
        user_id = current_user.id if current_user.is_authenticated else get_jwt_identity()
        comment = Comment(content=content, user_id=user_id, post_id=post_id, parent_id=parent_id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully')
        if request.accept_mimetypes.accept_html:
            return redirect(url_for('posts.get_post', post_id=post_id))
        return jsonify({'msg': 'Comment added', 'comment_id': comment.id}), 201
    return render_template('add_comment.html', post=post)
