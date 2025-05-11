
from flask import Blueprint, request, jsonify, abort, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import current_user, login_required
from app import db
from app.models import Post
from app.utils import paginate_query

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
@jwt_required(optional=True)
def create_post():
    if request.method == 'POST':
        data = request.form if request.form else request.get_json()
        title = data.get('title')
        content = data.get('content')
        tags = data.get('tags')  # Comma separated
        if not title or not content:
            flash('Title and content are required')
            return render_template('create_post.html')
        user_id = current_user.id if current_user.is_authenticated else get_jwt_identity()
        post = Post(title=title, content=content, tags=tags, user_id=user_id)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully')
        if request.accept_mimetypes.accept_html:
            return redirect(url_for('posts.get_post', post_id=post.id))
        return jsonify({'msg': 'Post created', 'post': {'id': post.id, 'title': post.title}}), 201
    return render_template('create_post.html')

@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.accept_mimetypes.accept_html:
        return render_template('post_detail.html', post=post)
    return jsonify({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'tags': post.tags,
        'created_at': post.created_at.isoformat(),
        'author': post.author.username
    })

@posts_bp.route('/<int:post_id>/edit', methods=['GET', 'POST', 'PUT'])
@login_required
@jwt_required(optional=True)
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = current_user.id if current_user.is_authenticated else get_jwt_identity()
    if post.user_id != user_id:
        abort(403, description="Not authorized to edit this post")
    if request.method in ['POST', 'PUT']:
        data = request.form if request.form else request.get_json()
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        post.tags = data.get('tags', post.tags)
        db.session.commit()
        flash('Post updated successfully')
        if request.accept_mimetypes.accept_html:
            return redirect(url_for('posts.get_post', post_id=post.id))
        return jsonify({'msg': 'Post updated'})
    return render_template('edit_post.html', post=post)

@posts_bp.route('/<int:post_id>/delete', methods=['POST', 'DELETE'])
@login_required
@jwt_required(optional=True)
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = current_user.id if current_user.is_authenticated else get_jwt_identity()
    if post.user_id != user_id:
        abort(403, description="Not authorized to delete this post")
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully')
    if request.accept_mimetypes.accept_html:
        return redirect(url_for('posts.list_posts'))
    return jsonify({'msg': 'Post deleted'})

@posts_bp.route('/', methods=['GET'])
def list_posts():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    query = Post.query.order_by(Post.created_at.desc())
    if search:
        query = query.filter(
            Post.title.contains(search) | 
            Post.content.contains(search) | 
            Post.tags.contains(search)
        )
    pagination = paginate_query(query, page)
    posts = pagination.items
    if request.accept_mimetypes.accept_html:
        return render_template('posts_list.html', posts=posts, pagination=pagination)
    posts_data = [{
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'tags': post.tags,
        'created_at': post.created_at.isoformat(),
        'author': post.author.username
    } for post in posts]
    return jsonify({'posts': posts_data, 'total': pagination.total})
