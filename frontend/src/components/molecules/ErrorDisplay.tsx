import React from 'react';

interface ErrorDisplayProps {
  message: string;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ message }) => (
  <div className="bg-red-100 text-red-700 px-4 py-2 rounded">{message}</div>
);
