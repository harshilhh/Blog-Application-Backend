
from flask import Blueprint, request, jsonify
from models.schema import *
from datetime import datetime, timedelta
import uuid
from functools import wraps
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os



api= Blueprint('api', __name__)
load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")  


@api.route('/createall', methods=['GET'])
def dbcreate():
    db.create_all()
    db.session.commit()
    return jsonify (message='All tables created successfully')



def generate_token(user_id):
    expiry = datetime.utcnow() + timedelta(days=1)
    token = jwt.encode(
        {'user_id': user_id, 'exp': expiry},
        SECRET_KEY,
        algorithm='HS256'
    )
    return token, expiry

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            token = token.split()[1]  # Remove 'Bearer' prefix
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
        except:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@api.route('/accounts', methods=['POST'])
def create_account():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400
    
    # Create new user
    try:
        new_user = User(
            name=data['name'],
            email=data['email']
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'Account created successfully',
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating account', 'error': str(e)}), 500

@api.route('/accounts/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    try:
        token, expiry = generate_token(user.id)
        
        # Update user's token info
        user.auth_token = token
        user.token_expiry = expiry
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

@api.route('/accounts', methods=['PUT'])
@token_required
def update_account(current_user):
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    try:
        # Update allowed fields
        if 'name' in data:
            current_user.name = data['name']
        if 'email' in data:
            # Check if new email already exists
            if User.query.filter(User.email == data['email'], User.id != current_user.id).first():
                return jsonify({'message': 'Email already in use'}), 400
            current_user.email = data['email']
        if 'password' in data:
            current_user.set_password(data['password'])
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Account updated successfully',
            'user': {
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating account', 'error': str(e)}), 500

@api.route('/accounts', methods=['DELETE'])
@token_required
def delete_account(current_user):
    try:
        db.session.delete(current_user)
        db.session.commit()
        return jsonify({'message': 'Account deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting account', 'error': str(e)}), 500

@api.route('/me', methods=['GET'])
@token_required
def get_user_info(current_user):
    return jsonify({
        'user': {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email,
            'created_at': current_user.created_at,
            'posts_count': len(current_user.posts),
            'likes_count': len(current_user.likes)
        }
    }), 200



@api.route('/blog', methods=['POST'])
@token_required
def create_blog(current_user):
    data = request.get_json()
    
    required_fields = ['title', 'content']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    try:
        new_post = Post(
            title=data['title'],
            description=data.get('description', ''),
            content=data['content'],
            is_public=data.get('is_public', True),
            user_id=current_user.id
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        return jsonify({
            'message': 'Blog created successfully',
            'post': {
                'id': new_post.id,
                'title': new_post.title,
                'description': new_post.description,
                'is_public': new_post.is_public,
                'created_at': new_post.created_at
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating blog', 'error': str(e)}), 500


@api.route('/blog', methods=['GET'])
@token_required
def get_all_blogs(current_user):
    try:
        # Get public posts and private posts owned by the current user
        posts = Post.query.filter(
            (Post.is_public == True) | 
            (Post.user_id == current_user.id)
        ).all()
        
        posts_data = []
        for post in posts:
            posts_data.append({
                'id': post.id,
                'title': post.title,
                'description': post.description,
                'is_public': post.is_public,
                'created_at': post.created_at,
                'author': {
                    'id': post.author.id,
                    'name': post.author.name
                },
                'likes_count': len(post.likes)
            })
        
        return jsonify({'posts': posts_data}), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching blogs', 'error': str(e)}), 500



@api.route('/blog/<int:post_id>', methods=['GET'])
@token_required
def get_blog_details(current_user, post_id):
    try:
        post = Post.query.get_or_404(post_id)
        
        # Check if user has access to private post
        if not post.is_public and post.user_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        return jsonify({
            'post': {
                'id': post.id,
                'title': post.title,
                'description': post.description,
                'content': post.content,
                'is_public': post.is_public,
                'created_at': post.created_at,
                'updated_at': post.updated_at,
                'author': {
                    'id': post.author.id,
                    'name': post.author.name
                },
                'likes': [{
                    'user_id': like.user_id,
                    'user_name': like.user.name,
                    'created_at': like.created_at
                } for like in post.likes]
            }
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching blog details', 'error': str(e)}), 500


@api.route('/blog/<int:post_id>', methods=['PUT'])
@token_required
def update_blog(current_user, post_id):
    post = Post.query.get_or_404(post_id)
    
    # Check if user owns the post
    if post.user_id != current_user.id:
        return jsonify({'message': 'Access denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    try:
        if 'title' in data:
            post.title = data['title']
        if 'description' in data:
            post.description = data['description']
        if 'content' in data:
            post.content = data['content']
        if 'is_public' in data:
            post.is_public = data['is_public']
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Blog updated successfully',
            'post': {
                'id': post.id,
                'title': post.title,
                'description': post.description,
                'is_public': post.is_public,
                'updated_at': post.updated_at
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating blog', 'error': str(e)}), 500



@api.route('/blog/<int:post_id>', methods=['DELETE'])
@token_required
def delete_blog(current_user, post_id):
    post = Post.query.get_or_404(post_id)
    
    # Check if user owns the post
    if post.user_id != current_user.id:
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Blog deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting blog', 'error': str(e)}), 500


@api.route('/like/<int:post_id>', methods=['POST'])
@token_required
def like_blog(current_user, post_id):
    post = Post.query.get_or_404(post_id)
    
    # Check if user has access to private post
    if not post.is_public and post.user_id != current_user.id:
        return jsonify({'message': 'Access denied'}), 403
    
    # Check if already liked
    existing_like = Like.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()
    
    if existing_like:
        return jsonify({'message': 'Blog already liked'}), 400
    
    try:
        new_like = Like(
            user_id=current_user.id,
            post_id=post_id
        )
        db.session.add(new_like)
        db.session.commit()
        
        return jsonify({'message': 'Blog liked successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error liking blog', 'error': str(e)}), 500

@api.route('/like/<int:post_id>', methods=['DELETE'])
@token_required
def unlike_blog(current_user, post_id):
    like = Like.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()
    
    if not like:
        return jsonify({'message': 'Like not found'}), 404
    
    try:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'message': 'Blog unliked successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error unliking blog', 'error': str(e)}), 500