import React, { useEffect } from 'react';
import axios from 'axios';
import MathResponse from '../../components/MathResponse';
import DiscussionBoard from '../../components/DiscussionBoard';
import { BASE_URL } from '../../config';
import Image from 'next/image'

export default async function QuestionPage(
  {
    params: { id },
  }: {
    params: { id: string }
  }
) {
  console.log('QuestionPage:id:', id);
  let question = null;
  let answer = null;

  const fetchQuestionAndAnswer = async () => {
    try {
      const response = await axios.get(BASE_URL + `/api/questions/${id}`);
      question = response.data.question;
      answer = response.data.answer
      const commentsResponse = await axios.get(BASE_URL + `/api/questions/${id}/comments`);

    } catch (error) {
      console.error('Error fetching question and answer:', error);
    }
  };

  await fetchQuestionAndAnswer();

  if (!question || !answer) {
    return <div>Loading...</div>;
  }

  return (
    <div className="question-page p-4">
      <h1 className="text-2xl font-bold mb-4">Question</h1>
        {question && question.type === 'link' ? (
          <Image
            src={question.question_text}
            width={500}
            height={500}
            alt="Picture of the author"
          />
          ) : (
        <p className="mb-4">{question.question_text}</p>
      )}
      <h2 className="text-xl font-semibold mb-2">Answer:</h2>
      <MathResponse response={answer && answer.content} />
      <DiscussionBoard questionId={question && question.id} />
    </div>
  );
};
