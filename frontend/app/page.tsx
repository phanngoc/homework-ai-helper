"use client";

// App.js show main component for homepage, task screenshot, upload image, and display answer
import React, { useState, useRef, useCallback, useEffect } from 'react';
import { useDispatch, useSelector, Provider } from 'react-redux';
import Webcam, { WebcamProps } from 'react-webcam';
import { setToken } from './reducers';
import DiscussionBoard from './components/DiscussionBoard';
import { RootState } from '@reduxjs/toolkit/query';
import store from './store';
import { getAnswer, uploadScreenshot } from './actions';

function App({  }) {
  const [file, setFile] = useState<File | null>(null);
  const [screenshot, setScreenshot] = useState(null);
  const [temporaryUrl, setTemporaryUrl] = useState(null);
  const dispatch = useDispatch();
  const answer = useSelector((state: RootState<any, any, any>) => state.answer);
  const webcamRef = useRef(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log('e.target.files:', e.target.files);
    if (e.target.files) {
      setFile(e.target.files[0]);
      dispatch(uploadScreenshot(e.target.files[0]));
    }
  };

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    console.log('urlParams:', urlParams);
    const token = urlParams.get('token');
    if (token) {
        localStorage.setItem('authToken', token);
        dispatch(setToken(token)); // Dispatch an action to save the token in the Redux store
    }
  }, []);

  const handleSubmit = (action : string) => {
      dispatch(getAnswer({action, temporaryUrl}));
  };

  const handleTakeScreenshot = useCallback(async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setScreenshot(imageSrc);
    dispatch(uploadScreenshot(imageSrc));
  }, [webcamRef]);

  const handleLogin = () => {
    window.location.href = `http://127.0.0.1:5000/login`;
  };

  return (
    <Provider store={store}>
      <div className="flex flex-col min-h-screen p-4">
        <h1 className="text-2xl font-bold mb-4">AI Homework Helper</h1>
        <button onClick={handleLogin} className="bg-blue-500 text-white px-4 py-2 rounded mb-4">
          Login with Google
        </button>
        <input type="file" onChange={handleFileChange} className="mb-4 p-2 border rounded" />
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          width={320}
          height={240}
          className="mb-4 border rounded"
        />
        <div className="flex space-x-2 mb-4">
          <button onClick={handleTakeScreenshot} className="bg-blue-500 text-white px-4 py-2 rounded">
            Take Screenshot
          </button>
          <button onClick={() => handleSubmit('resolve')} className="bg-green-500 text-white px-4 py-2 rounded">
            Resolve
          </button>
          <button onClick={() => handleSubmit('suggest')} className="bg-yellow-500 text-white px-4 py-2 rounded">
            Suggestion
          </button>
        </div>
        {answer && (
          <div className="answer-wrap p-4 border rounded">
            <h2 className="text-xl font-semibold mb-2">Answer:</h2>
            <p className="mb-4">{answer}</p>
            <DiscussionBoard questionId={answer.questionId} />
          </div>
        )}
      </div>
    </Provider>
  );
}

// Wrap the App component with the Provider and pass the store
export default function WrappedApp(props: any) {
  return (
    <Provider store={store}>
      <App {...props} />
    </Provider>
  );
}