from flask import Blueprint, request, jsonify
from .models import Comment, User
from .extensions import db
from flask import current_app
from .auth import token_required  # Updated import

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/questions/<int:question_id>/comments', methods=['GET'])
def get_comments(question_id):
    print('route:question_id', question_id)
    comments = Comment.query.filter_by(question_id=question_id).all()
    response_arr = [{
        'id': comment.id,
        'text': comment.text,
        'user': comment.user.to_dict(),
    } for comment in comments]

    return jsonify(response_arr)

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
        'user': current_user,
        'text': comment.text
    })
