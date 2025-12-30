'use client';

import { useState, useRef } from 'react';
import Icon from './Icon';
import { MAX_TEXT_LENGTH } from '@/app/lib/constants';

interface TextInputProps {
    value: string;
    onChange: (value: string) => void;
    onClear: () => void;
    placeholder?: string;
    disabled?: boolean;
}

export default function TextInput({
    value,
    onChange,
    onClear,
    placeholder = 'Enter or paste your text here to check for grammar, spelling, and punctuation errors...',
    disabled = false,
}: TextInputProps) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const [isFocused, setIsFocused] = useState(false);

    const characterCount = value.length;
    const isNearLimit = characterCount > MAX_TEXT_LENGTH * 0.9;
    const isOverLimit = characterCount > MAX_TEXT_LENGTH;

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const newValue = e.target.value;
        if (newValue.length <= MAX_TEXT_LENGTH) {
            onChange(newValue);
        }
    };

    return (
        <div className="relative">
            <div
                className={`
          relative bg-[var(--color-bg-800)] rounded-xl overflow-hidden
          border transition-all duration-200
          ${isFocused
                        ? 'border-[var(--color-text-300)] shadow-[0_0_0_3px_rgba(155,168,171,0.1)]'
                        : 'border-[var(--color-bg-600)]'
                    }
          ${disabled ? 'opacity-50' : ''}
        `}
            >
                <textarea
                    ref={textareaRef}
                    value={value}
                    onChange={handleChange}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    placeholder={placeholder}
                    disabled={disabled}
                    className="
            w-full min-h-[300px] md:min-h-[400px] p-4 md:p-6
            bg-transparent text-[var(--color-text-100)]
            font-['Raleway'] text-base leading-relaxed
            resize-none outline-none
            placeholder:text-[var(--color-bg-600)]
          "
                    spellCheck={false}
                />

                {/* Footer with character count and clear button */}
                <div className="flex items-center justify-between px-4 py-3 bg-[var(--color-bg-700)] border-t border-[var(--color-bg-600)]">
                    <span
                        className={`
              text-sm font-medium transition-colors
              ${isOverLimit
                                ? 'text-[var(--color-error-spelling)]'
                                : isNearLimit
                                    ? 'text-[var(--color-error-punctuation)]'
                                    : 'text-[var(--color-text-300)]'
                            }
            `}
                    >
                        {characterCount.toLocaleString()} / {MAX_TEXT_LENGTH.toLocaleString()} characters
                    </span>

                    {value.length > 0 && (
                        <button
                            onClick={onClear}
                            disabled={disabled}
                            className="
                btn btn-ghost text-[var(--color-text-300)]
                hover:text-[var(--color-text-100)] hover:bg-[var(--color-bg-600)]
                text-sm py-1.5 px-3
              "
                        >
                            <Icon name="trash" size={16} />
                            <span>Clear</span>
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
