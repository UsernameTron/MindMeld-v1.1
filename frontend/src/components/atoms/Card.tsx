import React from 'react';
import classNames from 'classnames';

export interface CardProps {
  className?: string;
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ className, children }) => (
  <div className={classNames('bg-white rounded shadow p-4', className)}>
    {children}
  </div>
);
