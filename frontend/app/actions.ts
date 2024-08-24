import axios, { AxiosResponse } from 'axios';
import { Dispatch } from 'redux';

const BASE_URL = 'http://127.0.0.1:5000';

const dataURLtoBlob = (dataurl: string) => {
  const arr = dataurl.split(',');
  const mime = arr[0].match(/:(.*?);/)[1];
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }
  return new Blob([u8arr], { type: mime });
};

export const uploadScreenshot = (imageSrc: string) => async (dispatch: Dispatch) => {
  try {
    const blob = dataURLtoBlob(imageSrc);
    const formData = new FormData();
    formData.append('file', blob);

    const response = await axios.post(BASE_URL + '/upload_screenshot', formData);
    dispatch({ type: 'UPLOAD_SCREENSHOT_SUCCESS', payload: response.data.temporary_url });
  } catch (error) {
    dispatch({ type: 'UPLOAD_SCREENSHOT_FAILURE', payload: error.message });
  }
};

// write function getAnswer from server
export const getAnswer = (action: string, temporaryUrl: string) => async (dispatch: Dispatch) => {
  try {
    const response = await axios.post(upload_screenshot + '/get_answer', { action, temporaryUrl });
    dispatch({ type: 'RETRIEVE_ANSWER_SUCCESS', payload: response.data.answer });
  } catch (error) {
    dispatch({ type: 'RETRIEVE_ANSWER_FAILURE', payload: error.message });
  }
};