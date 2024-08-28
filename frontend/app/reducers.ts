import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { getAnswer, uploadScreenshot } from './actions';

// Define the shape of the state
interface RootState {
  answer: string | null;
  error: string | null;
  imageSrc: string | null;
  token: string | null;
}

// Define the initial state with proper typing
const initialState: RootState = {
  answer: null,
  error: null,
  imageSrc: null,
  token: null,
};

// Create a slice
const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    retrieveAnswerSuccess(state, action: PayloadAction<string>) {
      state.answer = action.payload;
    },
    uploadScreenshotFailure(state, action: PayloadAction<string>) {
      state.error = action.payload;
    },
    uploadScreenshotSuccess(state, action: PayloadAction<string>) {
      state.imageSrc = action.payload;
    },
    setToken(state, action: PayloadAction<string>) {
      state.token = action.payload;
      localStorage.setItem('authToken', action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(uploadScreenshot.pending, (state) => {
        state.error = null;
      })
      .addCase(uploadScreenshot.fulfilled, (state, action: PayloadAction<string>) => {
        state.imageSrc = action.payload;
      })
      .addCase(uploadScreenshot.rejected, (state, action: PayloadAction<string>) => {
        state.error = action.payload;
      })
      .addCase(getAnswer.pending, (state) => { // Handle getAnswer.pending
        state.error = null;
      })
      .addCase(getAnswer.fulfilled, (state, action: PayloadAction<string>) => { // Handle getAnswer.fulfilled
        state.answer = action.payload;
      })
      .addCase(getAnswer.rejected, (state, action: PayloadAction<string>) => { // Handle getAnswer.rejected
        state.error = action.payload;
      });
  },
});

// Export actions
export const {
  retrieveAnswerSuccess,
  uploadScreenshotFailure,
  uploadScreenshotSuccess,
  setToken,
} = appSlice.actions;

// Export reducer
export default appSlice.reducer;