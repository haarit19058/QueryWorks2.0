
import React, { useState, useEffect, useRef } from 'react';
import { Search, MapPin } from 'lucide-react';
import { GEOAPIFY_API_KEY } from '../constants';
import { GeoLocation } from '../types';

interface AutocompleteProps {
  placeholder: string;
  onSelect: (location: GeoLocation) => void;
  value?: string;
}

export const Autocomplete: React.FC<AutocompleteProps> = ({ placeholder, onSelect, value = '' }) => {
  const [query, setQuery] = useState(value);
  const [suggestions, setSuggestions] = useState<GeoLocation[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setQuery(value);
  }, [value]);

  useEffect(() => {
    const timer = setTimeout(async () => {
      if (query.length > 2) {
        try {
          const response = await fetch(
            `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(query)}&apiKey=${GEOAPIFY_API_KEY}&filter=countrycode:in`
          );
          const data = await response.json();
          if (data.features) {
            setSuggestions(data.features.map((f: any) => ({
              lat: f.properties.lat,
              lon: f.properties.lon,
              display_name: f.properties.formatted
            })));
            setShowDropdown(true);
          }
        } catch (error) {
          console.error('Error fetching suggestions:', error);
        }
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative w-full" ref={dropdownRef}>
      <div className="relative">
        <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all text-slate-900 font-medium"
        />
      </div>
      {showDropdown && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-slate-200 rounded-lg shadow-xl max-h-60 overflow-y-auto">
          {suggestions.map((item, index) => (
            <button
              key={index}
              onClick={() => {
                onSelect(item);
                setQuery(item.display_name);
                setShowDropdown(false);
              }}
              className="w-full text-left px-4 py-3 hover:bg-slate-50 transition-colors border-b last:border-0 border-slate-100 flex items-start gap-3"
            >
              <Search className="w-4 h-4 text-slate-400 mt-1 flex-shrink-0" />
              <span className="text-sm text-slate-700 leading-tight">{item.display_name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
