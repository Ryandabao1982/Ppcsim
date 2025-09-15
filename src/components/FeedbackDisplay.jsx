// src/components/FeedbackDisplay.jsx
import React from 'react';
import '../styles/FeedbackDisplay.css';

/**
 * FeedbackDisplay Component
 *
 * This component is responsible for showing the AI-generated feedback
 * to the user. It breaks down the feedback into three clear categories:
 * - Strengths: What the user did well.
 * - Weaknesses: Areas for improvement.
 * - Pro-Tips: Actionable advice for better results.
 *
 * This is a key part of the learning experience, designed to be
 * encouraging and educational.
 */
const FeedbackDisplay = ({ feedback }) => {
  if (!feedback) {
    return null; // Don't render anything if there's no feedback yet
  }

  const { score, strengths, weaknesses, proTips } = feedback;

  return (
    <div className="feedback-container">
      <h2>Campaign Feedback</h2>
      <div className="feedback-score">
        Your Score: <span className="score-value">{score}/100</span>
      </div>
      <div className="feedback-section">
        <h3>Strengths</h3>
        <ul>
          {strengths.map((item, index) => <li key={index} className="strength">{item}</li>)}
        </ul>
      </div>
      <div className="feedback-section">
        <h3>Weaknesses</h3>
        <ul>
          {weaknesses.map((item, index) => <li key={index} className="weakness">{item}</li>)}
        </ul>
      </div>
      <div className="feedback-section">
        <h3>Pro-Tips</h3>
        <ul>
          {proTips.map((item, index) => <li key={index} className="protip">{item}</li>)}
        </ul>
      </div>
    </div>
  );
};

export default FeedbackDisplay;
