// CodeEditorProps schema
export interface CodeEditorProps {
  value?: string;
  language?: string;
  onChange?: (value: string | undefined) => void;
  height?: string | number;
  size?: 'small' | 'medium' | 'large';
  category?: 'analyze' | 'chat' | 'rewrite' | 'persona';
  readOnly?: boolean;
  className?: string;
  options?: Record<string, any>;
  theme?: 'light' | 'dark' | 'system';
  loadingComponent?: React.ReactNode;
}
