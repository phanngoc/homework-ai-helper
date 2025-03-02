import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import { BASE_URL } from './config';

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

      const response = await fetch(BASE_URL + '/upload_screenshot', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      return data.temporary_url;
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
      const response = await fetch(BASE_URL + '/api/answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Access-Token': token || '',
        },
        body: JSON.stringify({ action, imageSrc }),
      });

      if (!response.ok) {
        throw new Error('Failed to get answer');
      }

      const data = await response.json();
      console.log('getAnswer:response:', data);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);
