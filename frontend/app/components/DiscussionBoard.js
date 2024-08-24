// DiscussionBoard.js
import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import axios from 'axios';

const DiscussionBoard = ({ questionId }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const user = useSelector(state => state.user);

  useEffect(() => {
    const fetchComments = async () => {
      const response = await axios.get(`/questions/${questionId}/comments`);
      setComments(response.data);
    };
    fetchComments();
  }, [questionId]);

  const handleCommentSubmit = async () => {
    if (newComment.trim()) {
      const response = await axios.post(`/questions/${questionId}/comments`, {
        userId: user.id,
        text: newComment,
      });
      setComments([...comments, response.data]);
      setNewComment('');
    }
  };

  return (
    <div className="discussion-board">
      <h2>Discussion</h2>
      <div className="comments">
        {comments.map(comment => (
          <div key={comment.id} className="comment">
            <p><strong>{comment.user.email}:</strong> {comment.text}</p>
          </div>
        ))}
      </div>
      <div className="new-comment">
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Add a comment..."
        />
        <button onClick={handleCommentSubmit}>Post Comment</button>
      </div>
    </div>
  );
};

export default DiscussionBoard;