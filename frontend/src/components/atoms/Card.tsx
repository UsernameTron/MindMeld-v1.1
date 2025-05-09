import React from 'react';
import clsx from 'clsx';

export interface CardProps {
  className?: string;
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ className, children }) => (
  <div className={clsx('bg-white rounded shadow p-4', className)}>{children}</div>
);
