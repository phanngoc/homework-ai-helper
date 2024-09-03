import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { getAnswer, uploadScreenshot } from './actions';

// Define the shape of the state
interface RootState {
  answer: string | null;
  error: string | null;
  imageSrc: string | null;
  token: string | null;
  question: any | null; // Add question to the state
}

// Define the initial state with proper typing
const initialState: RootState = {
  answer: null,
  error: null,
  imageSrc: null,
  token: null,
  question: null, // Initialize question
};

// Create a slice
const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    retrieveAnswerSuccess(state, action: PayloadAction<any>) {
      state.answer = action.payload;
      console.log('retrieveAnswerSuccess:answer');
    },
    uploadScreenshotFailure(state, action: PayloadAction<string>) {
      state.error = action.payload;
    },
    uploadScreenshotSuccess(state, action: PayloadAction<string>) {
      console.log('uploadScreenshotSuccess:action', action);
      state.imageSrc = action.payload;
    },
    setToken(state, action: PayloadAction<string>) {
      state.token = action.payload;
      localStorage.setItem('authToken', action.payload);
    },
    setQuestion(state, action: PayloadAction<any>) { // Add setQuestion action
      state.question = action.payload;
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
      .addCase(getAnswer.fulfilled, (state, action: PayloadAction<any>) => { // Handle getAnswer.fulfilled
        state.answer = action.payload.answer;
        state.question = action.payload.question;
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
  setQuestion, // Export setQuestion action
} = appSlice.actions;

// Export reducer
export default appSlice.reducer;