// Polyfill ResizeObserver for jsdom+Recharts before any imports
if (typeof global !== 'undefined' && !global.ResizeObserver) {
  global.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}
if (typeof window !== 'undefined' && !window.ResizeObserver) {
  window.ResizeObserver = global.ResizeObserver;
}

// Polyfill ResizeObserver for Recharts/ResponsiveContainer
if (typeof window !== 'undefined' && !window.ResizeObserver) {
  window.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { SentimentVisualization, EmotionScores, SentimentVisualizationProps } from "./SentimentVisualization";

const mockEmotions: EmotionScores = {
  joy: 0.7,
  anger: 0.1,
  fear: 0.05,
  sadness: 0.05,
  surprise: 0.05,
  disgust: 0.05,
};

describe("SentimentVisualization", () => {
  const baseProps: SentimentVisualizationProps = {
    emotions: mockEmotions,
    sentiment: "positive",
    sentimentScore: 0.85,
    isLoading: false,
    error: null,
  };

  it("renders radar chart by default", () => {
    render(<SentimentVisualization {...baseProps} />);
    expect(screen.getByLabelText(/emotion radar chart/i)).toBeInTheDocument();
    // Radar chart should show all emotion labels
    Object.values(mockEmotions).forEach(() => {
      // Radar chart is SVG, so we check for axis labels
      expect(screen.getByText(/joy|anger|fear|sadness|surprise|disgust/i)).toBeInTheDocument();
    });
  });

  it("switches to gauge visualization when gauge button is clicked", () => {
    render(<SentimentVisualization {...baseProps} />);
    const gaugeBtn = screen.getByRole("tab", { name: /gauge/i });
    fireEvent.click(gaugeBtn);
    expect(screen.getByLabelText(/sentiment gauge/i)).toBeInTheDocument();
    expect(screen.getByText(/positive/i)).toBeInTheDocument();
  });

  it("switches to color scale visualization when color scale button is clicked", () => {
    render(<SentimentVisualization {...baseProps} />);
    const colorBtn = screen.getByRole("tab", { name: /color scale/i });
    fireEvent.click(colorBtn);
    expect(screen.getByLabelText(/emotion color scale/i)).toBeInTheDocument();
    // Color scale should show all emotion bars
    expect(screen.getAllByRole("progressbar")).toHaveLength(6);
  });

  it("handles missing emotion data gracefully", () => {
    render(<SentimentVisualization sentiment="neutral" sentimentScore={0.5} />);
    // Should still render toggles and gauge
    expect(screen.getByRole("tablist")).toBeInTheDocument();
    expect(screen.getByLabelText(/sentiment gauge/i)).toBeInTheDocument();
    expect(screen.getByText(/neutral/i)).toBeInTheDocument();
  });

  it("shows loading state", () => {
    render(<SentimentVisualization isLoading />);
    expect(screen.getByText(/loading analysis/i)).toBeInTheDocument();
  });

  it("shows error state", () => {
    render(<SentimentVisualization error="Something went wrong" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Something went wrong");
  });

  it("shows empty state if no data", () => {
    render(<SentimentVisualization />);
    expect(screen.getByText(/no analysis data available/i)).toBeInTheDocument();
  });

  it("applies correct color styling for each emotion bar", () => {
    render(<SentimentVisualization {...baseProps} />);
    fireEvent.click(screen.getByRole("tab", { name: /color scale/i }));
    const bars = screen.getAllByRole("progressbar");
    // Check that each bar has a style with a background color
    bars.forEach((bar) => {
      expect(bar).toHaveStyle("background");
    });
  });

  it("has correct ARIA attributes for accessibility", () => {
    render(<SentimentVisualization {...baseProps} />);
    // Tablist and tab roles
    expect(screen.getByRole("tablist")).toBeInTheDocument();
    expect(screen.getAllByRole("tab")).toHaveLength(3);
    // Tabpanel
    expect(screen.getByRole("tabpanel")).toBeInTheDocument();
    // Progressbars in color scale
    fireEvent.click(screen.getByRole("tab", { name: /color scale/i }));
    screen.getAllByRole("progressbar").forEach((bar) => {
      expect(bar).toHaveAttribute("aria-valuenow");
      expect(bar).toHaveAttribute("aria-valuemin", "0");
      expect(bar).toHaveAttribute("aria-valuemax", "100");
    });
  });
});
