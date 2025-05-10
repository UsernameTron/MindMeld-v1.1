import React from 'react';

const ThemeTester = () => {
  return (
    <div className="p-4 space-y-4">
      <h2 className="text-2xl font-bold">Theme Token Test</h2>
      <div className="space-y-2">
        <h3 className="text-xl">Brand Colors</h3>
        <div className="flex space-x-2">
          <div className="w-12 h-12 bg-primary-500 rounded"></div>
          <div className="w-12 h-12 bg-primary-600 rounded"></div>
          <div className="w-12 h-12 bg-primary-700 rounded"></div>
        </div>
      </div>
      <div className="space-y-2">
        <h3 className="text-xl">Feature Category Colors</h3>
        <div className="flex space-x-2">
          <div className="w-12 h-12 bg-analyze-default rounded"></div>
          <div className="w-12 h-12 bg-chat-default rounded"></div>
          <div className="w-12 h-12 bg-rewrite-default rounded"></div>
          <div className="w-12 h-12 bg-persona-default rounded"></div>
        </div>
      </div>
      <div className="space-y-2">
        <h3 className="text-xl">Typography</h3>
        <p className="text-xs">Extra Small Text</p>
        <p className="text-sm">Small Text</p>
        <p className="text-base">Base Text</p>
        <p className="text-lg">Large Text</p>
        <p className="text-xl">Extra Large Text</p>
      </div>
    </div>
  );
};

export default ThemeTester;
