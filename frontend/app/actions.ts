import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

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

// Create async thunks for the actions
export const uploadScreenshot = createAsyncThunk(
  'api/uploadScreenshot',
  async (imageSrc: string | File, { rejectWithValue }) => {
    try {
      let blob: Blob;
      if (typeof imageSrc === 'string') {
        // Convert base64 string to Blob
        blob = dataURLtoBlob(imageSrc);
      } else {
        // Use the File object directly
        blob = imageSrc;
      }

      const formData = new FormData();
      formData.append('file', blob);

      const response = await axios.post(BASE_URL + '/upload_screenshot', formData);
      return response.data.temporary_url;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const getAnswer = createAsyncThunk(
  'api/getAnswer',
  async ({ action, imageSrc }: { action: string; imageSrc: string }, { rejectWithValue }) => {
    const token = localStorage.getItem('authToken');
    console.log('getAnswer:token:', token, imageSrc);
    try {
      const response = await axios.post(BASE_URL + '/api/answer', { action, imageSrc }, {
        headers: {
          'x-access-token': token,
        },
      });
      console.log('getAnswer:response:', response);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);
