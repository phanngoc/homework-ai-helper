from flask import Blueprint, request, jsonify
from .models import Comment, User
from .extensions import db
from flask import current_app
from .auth import token_required  # Updated import

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/questions/<int:question_id>/comments', methods=['GET'])
def get_comments(question_id):
    comments = Comment.query.filter_by(question_id=question_id).all()
    return jsonify([{
        'id': comment.id,
        'user': {'id': comment.user.id, 'email': comment.user.email},
        'text': comment.text
    } for comment in comments])

@comments_bp.route('/questions/<int:question_id>/comments', methods=['POST'])
@token_required
def post_comment(current_user, question_id):
    data = request.json
    comment = Comment(
        question_id=question_id,
        user_id=current_user.id,
        text=data['text']
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({
        'id': comment.id,
        'user': {'id': comment.user.id, 'email': comment.user.email},
        'text': comment.text
    })
