import React, { Fragment, useMemo } from 'react';
import { Listbox, Transition } from '@headlessui/react';
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/react/20/solid';
import clsx from 'clsx';

export interface SelectOption {
  value: string;
  label: string;
  category?: 'analyze' | 'chat' | 'rewrite' | 'persona';
  disabled?: boolean;
  group?: string;
  icon?: React.ReactNode;
}

export interface SelectProps {
  options: SelectOption[];
  value?: string | string[];
  defaultValue?: string | string[];
  onChange?: (value: string | string[]) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: boolean;
  errorMessage?: string;
  size?: 'sm' | 'md' | 'lg';
  category?: 'analyze' | 'chat' | 'rewrite' | 'persona';
  multiple?: boolean;
  searchable?: boolean;
  loading?: boolean;
  required?: boolean;
  label?: string;
  className?: string;
  renderOption?: (option: SelectOption, selected: boolean) => React.ReactNode;
}

const sizeMap = {
  sm: 'py-1 px-2 text-sm',
  md: 'py-2 px-3 text-base',
  lg: 'py-3 px-4 text-lg',
};

const categoryMap = {
  analyze: 'border-blue-500 focus:ring-blue-500',
  chat: 'border-green-500 focus:ring-green-500',
  rewrite: 'border-yellow-500 focus:ring-yellow-500',
  persona: 'border-purple-500 focus:ring-purple-500',
};

export const Select: React.FC<SelectProps> = ({
  options,
  value,
  defaultValue,
  onChange,
  placeholder = 'Select...',
  disabled,
  error,
  errorMessage,
  size = 'md',
  category,
  multiple = false,
  searchable = false,
  loading = false,
  required,
  label,
  className,
  renderOption,
}) => {
  // Group options if any have a group
  const grouped = useMemo(() => {
    const groups: Record<string, SelectOption[]> = {};
    const ungrouped: SelectOption[] = [];
    options.forEach(opt => {
      if (opt.group) {
        if (!groups[opt.group]) groups[opt.group] = [];
        groups[opt.group].push(opt);
      } else {
        ungrouped.push(opt);
      }
    });
    return { groups, ungrouped };
  }, [options]);

  // Controlled/uncontrolled value
  const [internalValue, setInternalValue] = React.useState(defaultValue ?? (multiple ? [] : ''));
  const isControlled = value !== undefined;
  const selectedValue = isControlled ? value : internalValue;

  const handleChange = (val: any) => {
    if (!isControlled) setInternalValue(val);
    onChange?.(val);
  };

  // Filtering
  const [query, setQuery] = React.useState('');
  const filteredOptions = useMemo(() => {
    if (!searchable || !query) return options;
    return options.filter(opt =>
      opt.label.toLowerCase().includes(query.toLowerCase())
    );
  }, [options, query, searchable]);

  // Render
  return (
    <div className={clsx('w-full', className)}>
      {label && (
        <label className="block text-sm font-medium mb-1">{label}{required && <span className="text-red-500">*</span>}</label>
      )}
      <Listbox
        value={selectedValue}
        onChange={handleChange}
        multiple={multiple}
        disabled={disabled}
      >
        {({ open }) => (
          <div className="relative">
            <Listbox.Button
              className={clsx(
                'relative w-full cursor-pointer rounded-md border bg-white pr-10 text-left shadow-sm focus:outline-none focus:ring-2',
                sizeMap[size],
                category && categoryMap[category],
                error && 'border-red-500 focus:ring-red-500',
                disabled && 'bg-gray-100 text-gray-400 cursor-not-allowed',
                'transition-colors duration-150'
              )}
            >
              <span className="block truncate">
                {multiple && Array.isArray(selectedValue) && selectedValue.length > 0
                  ? selectedValue.map(val => {
                      const opt = options.find(o => o.value === val);
                      return (
                        <span key={val} className="inline-flex items-center bg-gray-200 rounded px-2 py-0.5 mr-1 text-xs">
                          {opt?.label}
                        </span>
                      );
                    })
                  : !multiple && selectedValue
                  ? options.find(o => o.value === selectedValue)?.label
                  : <span className="text-gray-400">{placeholder}</span>
                }
              </span>
              <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                <ChevronUpDownIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
              </span>
            </Listbox.Button>
            <Transition
              as={Fragment}
              show={open}
              leave="transition ease-in duration-100"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
            >
              <Listbox.Options className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                {searchable && (
                  <div className="px-2 py-1">
                    <input
                      className="w-full border rounded px-2 py-1 text-sm focus:outline-none"
                      placeholder="Search..."
                      value={query}
                      onChange={e => setQuery(e.target.value)}
                      autoFocus
                    />
                  </div>
                )}
                {Object.keys(grouped.groups).map(group => (
                  <div key={group}>
                    <div className="px-3 py-1 text-xs font-semibold text-gray-500 bg-gray-50">{group}</div>
                    {grouped.groups[group].map(option => (
                      <Listbox.Option
                        key={option.value}
                        value={option.value}
                        disabled={option.disabled}
                        className={({ active, selected, disabled }) =>
                          clsx(
                            'relative cursor-pointer select-none py-2 pl-10 pr-4',
                            active && 'bg-blue-100',
                            selected && 'font-semibold',
                            disabled && 'opacity-50 cursor-not-allowed'
                          )
                        }
                      >
                        {({ selected }) => (
                          <>
                            <span className={clsx('block truncate', selected && 'font-semibold')}>
                              {renderOption ? renderOption(option, selected) : option.label}
                            </span>
                            {selected ? (
                              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-600">
                                <CheckIcon className="h-5 w-5" aria-hidden="true" />
                              </span>
                            ) : null}
                          </>
                        )}
                      </Listbox.Option>
                    ))}
                  </div>
                ))}
                {filteredOptions.filter(opt => !opt.group).map(option => (
                  <Listbox.Option
                    key={option.value}
                    value={option.value}
                    disabled={option.disabled}
                    className={({ active, selected, disabled }) =>
                      clsx(
                        'relative cursor-pointer select-none py-2 pl-10 pr-4',
                        active && 'bg-blue-100',
                        selected && 'font-semibold',
                        disabled && 'opacity-50 cursor-not-allowed'
                      )
                    }
                  >
                    {({ selected }) => (
                      <>
                        <span className={clsx('block truncate', selected && 'font-semibold')}>
                          {renderOption ? renderOption(option, selected) : option.label}
                        </span>
                        {selected ? (
                          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-600">
                            <CheckIcon className="h-5 w-5" aria-hidden="true" />
                          </span>
                        ) : null}
                      </>
                    )}
                  </Listbox.Option>
                ))}
                {filteredOptions.length === 0 && (
                  <div className="px-4 py-2 text-gray-400 text-sm">No options found</div>
                )}
              </Listbox.Options>
            </Transition>
          </div>
        )}
      </Listbox>
      {error && errorMessage && (
        <div className="text-xs text-red-500 mt-1">{errorMessage}</div>
      )}
    </div>
  );
};
