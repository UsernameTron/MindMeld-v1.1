import React from 'react';
import Head from 'next/head';
import ThemeTester from '../src/components/test/ThemeTester';
import { DashboardLayout } from '../src/components/layout/DashboardLayout';

export default function DesignTestPage() {
  return (
    <>
      <Head>
        <title>Design System Test | MindMeld</title>
        <meta name="description" content="Testing page for design system components" />
      </Head>
      <DashboardLayout>
        <div className="container mx-auto py-8">
          <h1 className="text-3xl font-bold mb-6">Design System Test Page</h1>
          <ThemeTester />
        </div>
      </DashboardLayout>
    </>
  );
}