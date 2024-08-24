// Define the shape of the state
interface RootState {
  answer: string | null;
  error: string | null;
  imageSrc: string | null;
}

// Define the initial state with proper typing
const initialState: RootState = {
  answer: null,
  error: null,
  imageSrc: null,
};

// Define action types
const RETRIEVE_ANSWER_SUCCESS = 'RETRIEVE_ANSWER_SUCCESS';
const UPLOAD_SCREENSHOT_FAILURE = 'UPLOAD_SCREENSHOT_FAILURE';
// UPLOAD_SCREENSHOT_SUCCESS
const UPLOAD_SCREENSHOT_SUCCESS = 'UPLOAD_SCREENSHOT_SUCCESS';


// Refactor the reducer with proper typing
import { AnyAction } from 'redux';

export const rootReducer = (state = initialState, action: AnyAction): RootState => {
  switch (action.type) {
    case RETRIEVE_ANSWER_SUCCESS:
      return { ...state, answer: action.payload };
    case UPLOAD_SCREENSHOT_FAILURE:
      return { ...state, error: action.payload };
    case UPLOAD_SCREENSHOT_SUCCESS:
        return {
          ...state,
          imageSrc: action.payload,
        };
      // other cases
    default:
      return state;
  }
};
