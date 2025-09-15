// src/components/CampaignCreation.jsx

import React, { useState } from 'react';
import '../styles/CampaignCreation.css';

/**
 * CampaignCreation Component
 *
 * This component renders a form to create a new PPC campaign.
 * It's the first step in our simulation, gathering the essential details:
 * - Campaign Name: For easy identification.
 * - Campaign Type: To switch between 'auto' and 'manual' targeting.
 * - Daily Budget: To set the spending limit.
 *
 * We use the `useState` hook to manage the form data, keeping the component
 * self-contained and easy to manage.
 */
const CampaignCreation = ({ onNext }) => {
  // State to hold the campaign data
  const [campaignData, setCampaignData] = useState({
    campaignName: '',
    campaignType: 'manual',
    dailyBudget: 20,
  });

  // Handler to update state when form fields change
  const handleChange = (e) => {
    const { name, value } = e.target;
    setCampaignData(prevData => ({
      ...prevData,
      [name]: value,
    }));
  };

  // When the form is submitted, pass the data to the parent component.
  const handleSubmit = (e) => {
    e.preventDefault();
    onNext(campaignData);
  };

  return (
    <div className="campaign-creation-container">
      <h2>Create Your Campaign</h2>
      <p>Let's start with the basics. Every great campaign begins with a clear name, type, and budget.</p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="campaignName">Campaign Name</label>
          <input
            type="text"
            id="campaignName"
            name="campaignName"
            value={campaignData.campaignName}
            onChange={handleChange}
            placeholder="e.g., Summer Sale"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="campaignType">Campaign Type</label>
          <select
            id="campaignType"
            name="campaignType"
            value={campaignData.campaignType}
            onChange={handleChange}
          >
            <option value="manual">Manual</option>
            <option value="auto">Automatic</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="dailyBudget">Daily Budget ($)</label>
          <input
            type="number"
            id="dailyBudget"
            name="dailyBudget"
            value={campaignData.dailyBudget}
            onChange={handleChange}
            min="1"
            step="1"
            required
          />
        </div>

        <button type="submit" className="cta-button">Next: Configure Ad Group</button>
      </form>
    </div>
  );
};

export default CampaignCreation;
