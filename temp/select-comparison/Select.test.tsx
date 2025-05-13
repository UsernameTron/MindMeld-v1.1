import React, { ReactNode, useState, forwardRef, createContext, useContext, Fragment, ElementType, MouseEvent } from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { Select, SelectOption } from './Select.js';
import { vi } from 'vitest';

// Define types for mocked components and context
interface MockListboxRootProps {
  value: any;
  onChange: (value: any) => void;
  children: (bag: { open: boolean; disabled?: boolean; value?: any }) => ReactNode;
  multiple?: boolean;
  disabled?: boolean;
}

interface MockListboxSubComponentProps {
  // Only allow string for className, but cast to any in the mock to allow function
  className?: any;
}

interface MockListboxButtonProps extends MockListboxSubComponentProps {
  children?: ReactNode;
  onClick?: (event?: MouseEvent<HTMLButtonElement>) => void; // Changed to accept event
  disabled?: boolean;
}

interface MockListboxOptionsProps extends MockListboxSubComponentProps {
  children?: ReactNode;
}

interface MockListboxOptionProps extends MockListboxSubComponentProps {
  value: any;
  disabled?: boolean;
  onClick?: (event?: MouseEvent<HTMLLIElement>) => void; // Changed to accept event
  children: ReactNode | ((bag: { selected: boolean; active: boolean; disabled: boolean }) => ReactNode);
}

interface MockTransitionProps {
  show: boolean;
  children: ReactNode;
  as?: ElementType | typeof Fragment;
  leave?: string;
  leaveFrom?: string;
  leaveTo?: string;
}

interface ListboxContextValue {
  value: any;
  onChange: (value: any) => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  multiple?: boolean;
  disabled?: boolean; // Root Listbox disabled state
}

const ListboxContext = createContext<ListboxContextValue | null>(null);

vi.mock('@headlessui/react', async () => {
  const actualHeadlessUi = await vi.importActual('@headlessui/react');

  const MockListboxRoot = forwardRef<HTMLDivElement, MockListboxRootProps>(
    ({ value, onChange, children, multiple, disabled }, ref) => {
      const [isOpen, setIsOpen] = useState(false);
      const contextValue: ListboxContextValue = { value, onChange, isOpen, setIsOpen, multiple, disabled };
      
      const renderPropOutput = children({ open: isOpen, disabled, value });

      return (
        <ListboxContext.Provider value={contextValue}>
          <div ref={ref}>{renderPropOutput}</div>
        </ListboxContext.Provider>
      );
    }
  );
  MockListboxRoot.displayName = 'Listbox';

  const MockListboxButton = forwardRef<HTMLButtonElement, MockListboxButtonProps>(
    ({ children, onClick, disabled: buttonDisabled, ...props }, ref) => {
      const context = useContext(ListboxContext);
      if (!context) throw new Error('Listbox.Button must be used within a Listbox');
      const effectivelyDisabled = context.disabled || buttonDisabled;
      return (
        <button
          ref={ref}
          {...props}
          type="button"
          disabled={effectivelyDisabled}
          onClick={(e) => { // e is MouseEvent<HTMLButtonElement>
            if (!effectivelyDisabled) {
              context.setIsOpen(!context.isOpen);
            }
            if (onClick) onClick(e);
          }}
        >
          {children}
        </button>
      );
    }
  );
  MockListboxButton.displayName = 'Listbox.Button';

  const MockListboxOptions = forwardRef<HTMLUListElement, MockListboxOptionsProps>(
    ({ children, ...props }, ref) => {
      const context = useContext(ListboxContext);
      if (!context) throw new Error('Listbox.Options must be used within a Listbox');
      return context.isOpen ? <ul ref={ref} {...props} role="listbox">{children}</ul> : null;
    }
  );
  MockListboxOptions.displayName = 'Listbox.Options';

  const MockListboxOption = forwardRef<HTMLLIElement, MockListboxOptionProps>(
    ({ children, value: optionValue, disabled: optionDisabledProp, onClick: optionOnClick, ...props }, ref) => {
      const context = useContext(ListboxContext);
      if (!context) throw new Error('Listbox.Option must be used within a Listbox');

      const effectiveDisabled = context.disabled || optionDisabledProp;

      const handleClick = (e: MouseEvent<HTMLLIElement>) => {
        if (effectiveDisabled) return;

        if (context.multiple) {
          const currentValues = Array.isArray(context.value) ? context.value : [];
          const newValue = currentValues.includes(optionValue)
            ? currentValues.filter((v: any) => v !== optionValue)
            : [...currentValues, optionValue];
          context.onChange(newValue);
        } else {
          context.onChange(optionValue);
        }
        context.setIsOpen(false);
        if (optionOnClick) optionOnClick(e);
      };

      const selected = context.multiple
        ? Array.isArray(context.value) && context.value.includes(optionValue)
        : context.value === optionValue;
      
      const optionRenderOutput = typeof children === 'function'
        ? (children as (bag: { selected: boolean; active: boolean; disabled: boolean }) => ReactNode)({ selected, active: false, disabled: !!effectiveDisabled })
        : children;

      let className = props.className;
      if (typeof className === 'function') {
        className = className({ active: false, selected, disabled: !!effectiveDisabled });
      }
      // Remove className from props to avoid React warning
      const { className: _ignoredClassName, ...restProps } = props;
      return <li ref={ref} {...restProps} className={className} onClick={handleClick} role="option" aria-selected={selected} aria-disabled={effectiveDisabled ? "true" : undefined} tabIndex={-1}>{optionRenderOutput}</li>;
    }
  );
  MockListboxOption.displayName = 'Listbox.Option';

  (MockListboxRoot as any).Button = MockListboxButton;
  (MockListboxRoot as any).Options = MockListboxOptions;
  (MockListboxRoot as any).Option = MockListboxOption;

  const MockTransition = forwardRef<any, MockTransitionProps>(
    ({ show, children, as, ...props }, ref) => {
      if (!show) return null;
      const AsComponent = as || 'div';

      if (AsComponent === Fragment) {
        return <>{children}</>;
      }
      return <AsComponent ref={ref} {...props}>{children}</AsComponent>;
    }
  );
  MockTransition.displayName = 'Transition';

  return {
    ...actualHeadlessUi,
    Listbox: MockListboxRoot,
    Transition: MockTransition,
  };
});

describe('Select', () => {
  const options: SelectOption[] = [
    { value: '1', label: 'One' },
    { value: '2', label: 'Two' },
    { value: '3', label: 'Three', disabled: true },
  ];

  afterEach(() => {
    vi.clearAllMocks();
    vi.resetModules(); 
  });

  it('renders and opens/closes via mouse', () => {
    render(<Select options={options} placeholder="Test Placeholder" />);
    const button = screen.getByRole('button');
    expect(screen.getByText('Test Placeholder')).toBeTruthy();

    fireEvent.click(button);
    expect(screen.getByRole('listbox')).toBeTruthy();
    expect(screen.getByText('One')).toBeTruthy();
    expect(screen.getByText('Two')).toBeTruthy();
    
    fireEvent.click(button); 
    expect(screen.queryByRole('listbox')).toBeFalsy();
    expect(screen.queryByText('One')).toBeFalsy();
  });

  it('selects an item and fires onChange', () => {
    const handleChange = vi.fn();
    render(<Select options={options} onChange={handleChange} />); 
    const button = screen.getByRole('button');
    expect(screen.getByText('Select...')).toBeTruthy();
    fireEvent.click(button); 

    const optionTwo = screen.getByText('Two');
    fireEvent.click(optionTwo);

    expect(handleChange).toHaveBeenCalledWith('2');
    expect(screen.queryByRole('listbox')).toBeFalsy(); 
    expect(screen.getByText('Two')).toBeTruthy(); 
    expect(screen.queryByText('Select...')).toBeFalsy();
  });

  it('disabled state prevents interaction', () => {
    render(<Select options={options} disabled />);
    const button = screen.getByRole('button');
    expect(button.hasAttribute('disabled')).toBe(true);
    fireEvent.click(button);
    expect(screen.queryByRole('listbox')).toBeFalsy();
  });

  it('does not select a disabled option', () => {
    const handleChange = vi.fn();
    render(<Select options={options} onChange={handleChange} placeholder="Select..." />);
    const button = screen.getByRole('button');
    fireEvent.click(button); 

    const optionThree = screen.getByRole('option', { name: 'Three' });
    expect(optionThree?.getAttribute("aria-disabled")).toBe("true");
    fireEvent.click(optionThree);

    expect(handleChange).not.toHaveBeenCalled();
    expect(screen.getByRole('listbox')).toBeTruthy(); 
    expect(screen.getByText('One')).toBeTruthy(); 
    expect(screen.getByText('Select...')).toBeTruthy(); 
  });

  it('opens with Enter key on button (mocked by click) and selects with Enter on option (mocked by click)', () => {
    const handleChange = vi.fn();
    render(<Select options={options} onChange={handleChange} />); 
    const button = screen.getByRole('button');
    button.focus();

    fireEvent.click(button);
    expect(screen.getByRole('listbox')).toBeTruthy();
    expect(screen.getByText('One')).toBeTruthy();

    const optionOne = screen.getByText('One');
    fireEvent.click(optionOne);

    expect(handleChange).toHaveBeenCalledWith('1');
    expect(screen.queryByRole('listbox')).toBeFalsy(); 
    expect(screen.getByText('One')).toBeTruthy(); 
  });

  it('closes with Escape key (mocked by button click)', () => {
    render(<Select options={options} />);
    const button = screen.getByRole('button');
    fireEvent.click(button); 
    expect(screen.getByRole('listbox')).toBeTruthy();

    fireEvent.click(button); 
    expect(screen.queryByRole('listbox')).toBeFalsy();
  });
});
