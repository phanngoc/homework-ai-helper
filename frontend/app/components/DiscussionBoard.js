"use client";

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BASE_URL } from '../config';
import { getTokenFromLocalStorage } from '../utils/token';

const DiscussionBoard = ({ questionId }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const token = getTokenFromLocalStorage();
  console.log('DiscussionBoard:token', token, questionId);
  useEffect(() => {
    const fetchComments = async () => {
      const response = await axios.get(BASE_URL + `/api/questions/${questionId}/comments`);
      setComments(response.data);
    };
    console.log('DiscussionBoard:fetchComments', questionId);
    fetchComments();
  }, []);

  const handleCommentSubmit = async () => {
    if (newComment.trim()) {
      const response = await axios.post(BASE_URL + `/api/questions/${questionId}/comments`, {
        text: newComment,
      }, {
        headers: {
          'x-access-token': token
        }
      });
      setComments([...comments, response.data]);
      setNewComment('');
    }
  };

  return (
    <div className="discussion-board p-4 bg-white shadow-md rounded-md">
      <h2 className="text-xl font-semibold mb-4">Discussion</h2>
      <div className="comments space-y-4">
        {comments.map(comment => (
          <div key={comment.id} className="comment p-2 bg-gray-100 rounded-md">
            <p className="text-sm"><strong>{comment.user.name}:</strong> {comment.text}</p>
          </div>
        ))}
      </div>
      <div className="new-comment mt-4">
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Add a comment..."
          className="w-full p-2 border rounded-md mb-2"
        />
        <button
          onClick={handleCommentSubmit}
          className="bg-blue-500 text-white px-4 py-2 rounded-md"
        >
          Post Comment
        </button>
      </div>
    </div>
  );
};

export default DiscussionBoard;