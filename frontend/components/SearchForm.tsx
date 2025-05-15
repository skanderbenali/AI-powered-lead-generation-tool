import React, { useState, ChangeEvent, FormEvent } from 'react';

type SearchFormProps = {
  onSearch: (criteria: any) => void;
};

const SearchForm = ({ onSearch }: SearchFormProps) => {
  const [criteria, setCriteria] = useState({
    industry: '',
    title: '',
    location: '',
    companySize: '',
    keywords: '',
  });

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setCriteria((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSearch(criteria);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 md:space-y-0 md:grid md:grid-cols-4 md:gap-4">
      <div>
        <label htmlFor="industry" className="block text-sm font-medium text-gray-700">
          Industry
        </label>
        <select
          id="industry"
          name="industry"
          value={criteria.industry}
          onChange={handleChange}
          className="input-field"
        >
          <option value="">Any Industry</option>
          <option value="technology">Technology</option>
          <option value="healthcare">Healthcare</option>
          <option value="finance">Finance</option>
          <option value="education">Education</option>
          <option value="manufacturing">Manufacturing</option>
          <option value="retail">Retail</option>
        </select>
      </div>

      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Job Title
        </label>
        <input
          type="text"
          id="title"
          name="title"
          placeholder="CEO, CTO, VP Sales, etc."
          value={criteria.title}
          onChange={handleChange}
          className="input-field"
        />
      </div>

      <div>
        <label htmlFor="location" className="block text-sm font-medium text-gray-700">
          Location
        </label>
        <input
          type="text"
          id="location"
          name="location"
          placeholder="City, State, Country"
          value={criteria.location}
          onChange={handleChange}
          className="input-field"
        />
      </div>

      <div>
        <label htmlFor="companySize" className="block text-sm font-medium text-gray-700">
          Company Size
        </label>
        <select
          id="companySize"
          name="companySize"
          value={criteria.companySize}
          onChange={handleChange}
          className="input-field"
        >
          <option value="">Any Size</option>
          <option value="1-10">1-10 employees</option>
          <option value="11-50">11-50 employees</option>
          <option value="51-200">51-200 employees</option>
          <option value="201-500">201-500 employees</option>
          <option value="501-1000">501-1000 employees</option>
          <option value="1001+">1001+ employees</option>
        </select>
      </div>

      <div className="md:col-span-3">
        <label htmlFor="keywords" className="block text-sm font-medium text-gray-700">
          Keywords
        </label>
        <input
          type="text"
          id="keywords"
          name="keywords"
          placeholder="AI, machine learning, blockchain, etc."
          value={criteria.keywords}
          onChange={handleChange}
          className="input-field"
        />
      </div>

      <div className="flex items-end">
        <button type="submit" className="btn-primary w-full">
          Search Leads
        </button>
      </div>
    </form>
  );
};

export default SearchForm;
