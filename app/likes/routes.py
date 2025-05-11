
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import current_user, login_required
from app import db
from app.models import Post, Comment, User

likes_bp = Blueprint('likes', __name__)

@likes_bp.route('/post/<int:post_id>', methods=['POST'])
@login_required
@jwt_required()
def toggle_post_like(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = current_user.id if current_user.is_authenticated else get_jwt_identity()
    user = post.liked_by.filter_by(id=user_id).first()
    if user:
        post.liked_by.remove(user)
        action = 'unliked'
    else:
        liker = User.query.get(user_id)
        post.liked_by.append(liker)
        action = 'liked'
    db.session.commit()
    return jsonify({'msg': f'Post {action}'})

@likes_bp.route('/comment/<int:comment_id>', methods=['POST'])
@login_required
@jwt_required()
def toggle_comment_like(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    user_id = current_user.id if current_user.is_authenticated else get_jwt_identity()
    user = comment.liked_by.filter_by(id=user_id).first()
    if user:
        comment.liked_by.remove(user)
        action = 'unliked'
    else:
        liker = User.query.get(user_id)
        comment.liked_by.append(liker)
        action = 'liked'
    db.session.commit()
    return jsonify({'msg': f'Comment {action}'})
