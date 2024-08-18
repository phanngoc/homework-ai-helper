// App.js
import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { uploadScreenshot, fetchAnswer } from './actions';

function App() {
  const [file, setFile] = useState(null);
  const dispatch = useDispatch();
  const answer = useSelector(state => state.answer);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = () => {
    dispatch(uploadScreenshot(file));
  };

  return (
    <div className="App">
      <h1>Brainly: AI Homework Helper</h1>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleSubmit}>Upload</button>
      {answer && <div><h2>Answer:</h2><p>{answer}</p></div>}
    </div>
  );
}

export default App;


