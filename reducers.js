// reducers.js
const initialState = {
  answer: null,
};

export const rootReducer = (state = initialState, action) => {
  switch (action.type) {
    case 'FETCH_ANSWER_SUCCESS':
      return { ...state, answer: action.payload };
    default:
      return state;
  }
};
