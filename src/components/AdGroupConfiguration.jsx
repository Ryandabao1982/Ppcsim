// src/components/AdGroupConfiguration.jsx
import React, { useState } from 'react';
import '../styles/AdGroupConfiguration.css';

// Dummy product data, as provided in the project brief.
// In a real application, this would likely come from an API.
const products = [
  { id: "SKU-001", name: "Wireless Earbuds" },
  { id: "SKU-002", name: "Yoga Mat" },
  { id: "SKU-003", name: "Coffee Grinder" },
];

/**
 * AdGroupConfiguration Component
 *
 * This component allows users to configure an ad group for their campaign.
 * This includes setting an ad group name, a default bid for clicks,
 * and selecting which products to include in this group.
 *
 * This step is crucial for organizing a campaign into logical themes or product categories.
 */
const AdGroupConfiguration = ({ onNext }) => {
  const [adGroupData, setAdGroupData] = useState({
    adGroupName: '',
    defaultBid: 1.2,
    selectedProducts: [],
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setAdGroupData(prevData => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleProductSelection = (productId) => {
    setAdGroupData(prevData => {
      const selectedProducts = prevData.selectedProducts.includes(productId)
        ? prevData.selectedProducts.filter(id => id !== productId)
        : [...prevData.selectedProducts, productId];
      return { ...prevData, selectedProducts };
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onNext(adGroupData);
  };

  return (
    <div className="ad-group-container">
      <h2>Configure Your Ad Group</h2>
      <p>Now, let's set up an ad group. Think of this as a container for a specific set of products and their targeting.</p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="adGroupName">Ad Group Name</label>
          <input
            type="text"
            id="adGroupName"
            name="adGroupName"
            value={adGroupData.adGroupName}
            onChange={handleChange}
            placeholder="e.g., High-Performance Yoga Mats"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="defaultBid">Default Bid ($)</label>
          <input
            type="number"
            id="defaultBid"
            name="defaultBid"
            value={adGroupData.defaultBid}
            onChange={handleChange}
            min="0.02"
            step="0.01"
            required
          />
        </div>

        <div className="form-group">
          <label>Select Products</label>
          <div className="product-list">
            {products.map(product => (
              <div key={product.id} className="product-item">
                <input
                  type="checkbox"
                  id={product.id}
                  checked={adGroupData.selectedProducts.includes(product.id)}
                  onChange={() => handleProductSelection(product.id)}
                />
                <label htmlFor={product.id}>{product.name}</label>
              </div>
            ))}
          </div>
        </div>

        <button type="submit" className="cta-button">Next: Set Up Targeting</button>
      </form>
    </div>
  );
};

export default AdGroupConfiguration;
