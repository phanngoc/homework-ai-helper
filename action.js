// actions.js
import axios from 'axios';

export const uploadScreenshot = (file) => async dispatch => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post('/upload', formData);
  dispatch({ type: 'FETCH_ANSWER_SUCCESS', payload: response.data.answer });
};
