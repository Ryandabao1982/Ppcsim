// src/components/TargetingSimulation.jsx
import React, { useState } from 'react';
import '../styles/TargetingSimulation.css';

/**
 * TargetingSimulation Component
 *
 * This is where the user defines how their ads will be targeted.
 * The UI adapts based on the campaign type ('manual' vs. 'auto').
 *
 * - Manual Targeting: Users can add specific keywords and choose their match type.
 *   This gives them fine-grained control over when their ads appear.
 * - Automatic Targeting: Users can leverage Amazon's algorithm by selecting
 *   different automatic targeting strategies.
 *
 * We'll pass the campaignType as a prop to determine which UI to show.
 */
const TargetingSimulation = ({ campaignType = 'manual', onNext }) => {
  // State for manual targeting
  const [keywords, setKeywords] = useState([]);
  const [currentKeyword, setCurrentKeyword] = useState('');
  const [matchType, setMatchType] = useState('phrase');

  // State for automatic targeting
  const [autoTargeting, setAutoTargeting] = useState({
    closeMatch: true,
    looseMatch: false,
    substitutes: false,
    complements: true,
  });

  const handleAddKeyword = () => {
    if (currentKeyword.trim() === '') return;
    setKeywords([...keywords, { text: currentKeyword, matchType }]);
    setCurrentKeyword('');
  };

  const handleAutoTargetingChange = (e) => {
    const { name, checked } = e.target;
    setAutoTargeting(prev => ({ ...prev, [name]: checked }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const targetingData = campaignType === 'manual'
      ? { manualKeywords: keywords }
      : { autoTargeting };
    onNext(targetingData);
  };

  const renderManualTargeting = () => (
    <>
      <h3>Manual Targeting</h3>
      <p>Add keywords to target specific customer searches.</p>
      <div className="keyword-form">
        <input
          type="text"
          value={currentKeyword}
          onChange={(e) => setCurrentKeyword(e.target.value)}
          placeholder="e.g., eco-friendly yoga mat"
        />
        <select value={matchType} onChange={(e) => setMatchType(e.target.value)}>
          <option value="broad">Broad</option>
          <option value="phrase">Phrase</option>
          <option value="exact">Exact</option>
        </select>
        <button type="button" onClick={handleAddKeyword}>Add Keyword</button>
      </div>
      <div className="keyword-list">
        <h4>Your Keywords:</h4>
        <ul>
          {keywords.length === 0 && <li className="no-keywords">No keywords added yet.</li>}
          {keywords.map((kw, index) => (
            <li key={index}>
              "{kw.text}" <span className={`match-type ${kw.matchType}`}>{kw.matchType}</span>
            </li>
          ))}
        </ul>
      </div>
    </>
  );

  const renderAutoTargeting = () => (
    <>
      <h3>Automatic Targeting</h3>
      <p>Let Amazon's algorithm find relevant searches for you.</p>
      <div className="auto-targeting-options">
        <div className="option-item">
          <input type="checkbox" id="closeMatch" name="closeMatch" checked={autoTargeting.closeMatch} onChange={handleAutoTargetingChange} />
          <label htmlFor="closeMatch">Close Match</label>
        </div>
        <div className="option-item">
          <input type="checkbox" id="looseMatch" name="looseMatch" checked={autoTargeting.looseMatch} onChange={handleAutoTargetingChange} />
          <label htmlFor="looseMatch">Loose Match</label>
        </div>
        <div className="option-item">
          <input type="checkbox" id="substitutes" name="substitutes" checked={autoTargeting.substitutes} onChange={handleAutoTargetingChange} />
          <label htmlFor="substitutes">Substitutes</label>
        </div>
        <div className="option-item">
          <input type="checkbox" id="complements" name="complements" checked={autoTargeting.complements} onChange={handleAutoTargetingChange} />
          <label htmlFor="complements">Complements</label>
        </div>
      </div>
    </>
  );

  return (
    <form className="targeting-container" onSubmit={handleSubmit}>
      <h2>Set Up Your Targeting</h2>
      {campaignType === 'manual' ? renderManualTargeting() : renderAutoTargeting()}
       <button type="submit" className="cta-button">Next: Get Feedback</button>
    </form>
  );
};

export default TargetingSimulation;
