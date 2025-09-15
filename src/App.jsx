import React, { useState } from 'react';
import CampaignCreation from './components/CampaignCreation';
import AdGroupConfiguration from './components/AdGroupConfiguration';
import TargetingSimulation from './components/TargetingSimulation';
import FeedbackDisplay from './components/FeedbackDisplay';
import './App.css';

import { generateFeedback } from './logic/feedback';

function App() {
  const [step, setStep] = useState(1); // 1: Campaign, 2: AdGroup, 3: Targeting, 4: Feedback
  const [campaignData, setCampaignData] = useState(null);
  const [adGroupData, setAdGroupData] = useState(null);
  const [targetingData, setTargetingData] = useState(null);
  const [feedback, setFeedback] = useState(null);

  const handleNext = (data) => {
    if (step === 1) {
      setCampaignData(data);
      setStep(2);
    } else if (step === 2) {
      setAdGroupData(data);
      setStep(3);
    } else if (step === 3) {
      setTargetingData(data);

      // Construct the final campaign object from all the steps
      const finalCampaign = {
        ...campaignData,
        adGroups: [{ ...adGroupData, targeting: data }]
      };

      // Generate the feedback using our new logic
      const newFeedback = generateFeedback(finalCampaign);
      setFeedback(newFeedback);
      setStep(4);
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return <CampaignCreation onNext={handleNext} />;
      case 2:
        return <AdGroupConfiguration onNext={handleNext} />;
      case 3:
        // Pass campaignType to TargetingSimulation so it can show the correct UI
        return <TargetingSimulation onNext={handleNext} campaignType={campaignData?.campaignType || 'manual'} />;
      case 4:
        return <FeedbackDisplay feedback={feedback} />;
      default:
        return <CampaignCreation onNext={handleNext} />;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>PPC Sim</h1>
      </header>
      <main className="step-container">
        <div className="step-content">
          {renderStep()}
        </div>
      </main>
    </div>
  );
}

export default App;
