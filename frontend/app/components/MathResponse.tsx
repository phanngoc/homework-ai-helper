import React from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

interface Step {
  explanation: string;
  output: string;
}

interface MathResponse {
  steps: Step[];
  final_answer: string;
}

interface MathResponseComponentProps {
  response: MathResponse;
}

const MathResponseComponent: React.FC<MathResponseComponentProps> = ({ response }) => {
  console.log('MathResponseComponent:response:', response);
  const { final_answer, steps } = response;

  return (
    <div className="math-response p-4 border rounded">
      <div className="steps mb-4">
        {steps.map((step, index) => (
          <div key={index} className="step mb-2">
            <div className="explanation mb-1">
              <strong>Explanation:</strong> <br />
              <ReactMarkdown rehypePlugins={[rehypeKatex]}>{step.explanation}</ReactMarkdown>
            </div>
            <div className="output">
              <strong>Output:</strong><br /> 
              <ReactMarkdown rehypePlugins={[rehypeKatex]}>{step.output}</ReactMarkdown>
            </div>
          </div>
        ))}
      </div>
      <div className="final-answer">
        <h3 className="text-lg font-semibold">Final Answer:</h3>
        <p>{final_answer}</p>
      </div>
    </div>
  );
};

export default MathResponseComponent;