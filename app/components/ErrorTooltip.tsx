'use client';

import { useState, useRef, useEffect } from 'react';
import { GrammarError } from '@/app/types/analysis';
import { ERROR_TYPE_LABELS, ERROR_TYPE_DESCRIPTIONS } from '@/app/lib/constants';
import Icon from './Icon';

interface ErrorTooltipProps {
    error: GrammarError;
    position: { x: number; y: number };
    onClose: () => void;
    onApplyFix: (error: GrammarError) => void;
}

export default function ErrorTooltip({
    error,
    position,
    onClose,
    onApplyFix,
}: ErrorTooltipProps) {
    const tooltipRef = useRef<HTMLDivElement>(null);
    const [adjustedPosition, setAdjustedPosition] = useState(position);

    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (tooltipRef.current && !tooltipRef.current.contains(e.target as Node)) {
                onClose();
            }
        };

        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                onClose();
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        document.addEventListener('keydown', handleEscape);

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
            document.removeEventListener('keydown', handleEscape);
        };
    }, [onClose]);

    useEffect(() => {
        if (tooltipRef.current) {
            const rect = tooltipRef.current.getBoundingClientRect();
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;

            let newX = position.x;
            let newY = position.y;

            if (position.x + rect.width > viewportWidth - 20) {
                newX = viewportWidth - rect.width - 20;
            }
            if (position.x < 20) {
                newX = 20;
            }

            if (position.y + rect.height > viewportHeight - 20) {
                newY = position.y - rect.height - 30;
            }

            setAdjustedPosition({ x: newX, y: newY });
        }
    }, [position]);

    const getErrorColor = (type: string) => {
        switch (type) {
            case 'spelling':
                return 'var(--color-error-spelling)';
            case 'grammar':
                return 'var(--color-error-grammar)';
            case 'punctuation':
                return 'var(--color-error-punctuation)';
            default:
                return 'var(--color-text-300)';
        }
    };

    const getIconName = (type: string): 'spell-check' | 'book-open' | 'type' => {
        switch (type) {
            case 'spelling':
                return 'spell-check';
            case 'grammar':
                return 'book-open';
            case 'punctuation':
                return 'type';
            default:
                return 'book-open';
        }
    };

    return (
        <div
            ref={tooltipRef}
            className="tooltip fixed z-50"
            style={{
                left: adjustedPosition.x,
                top: adjustedPosition.y,
            }}
        >
            <div className="space-y-3">
                {/* Header */}
                <div className="flex items-center gap-2">
                    <div
                        className="w-8 h-8 rounded-lg flex items-center justify-center"
                        style={{ backgroundColor: `${getErrorColor(error.type)}20` }}
                    >
                        <Icon
                            name={getIconName(error.type)}
                            size={16}
                            className="opacity-90"
                            color={getErrorColor(error.type)}
                        />
                    </div>
                    <div>
                        <p
                            className="text-xs font-semibold uppercase tracking-wide"
                            style={{ color: getErrorColor(error.type) }}
                        >
                            {ERROR_TYPE_LABELS[error.type]}
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="ml-auto text-[var(--color-text-300)] hover:text-[var(--color-text-100)] transition-colors"
                    >
                        <Icon name="x-circle" size={18} />
                    </button>
                </div>

                {/* Content */}
                <div className="space-y-2">
                    <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-[var(--color-error-spelling)] line-through text-sm">
                            {error.original}
                        </span>
                        <Icon name="chevron-right" size={14} className="text-[var(--color-text-300)]" />
                        <span className="text-[var(--color-success)] font-medium text-sm">
                            {error.suggestion}
                        </span>
                    </div>

                    <p className="text-xs text-[var(--color-text-300)]">
                        {error.explanation || ERROR_TYPE_DESCRIPTIONS[error.type]}
                    </p>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-1">
                    <button
                        onClick={() => onApplyFix(error)}
                        className="btn btn-primary text-xs py-1.5 flex-1"
                    >
                        <Icon name="check-circle" size={14} />
                        <span>Apply Fix</span>
                    </button>
                    <button
                        onClick={onClose}
                        className="btn btn-ghost text-xs py-1.5"
                    >
                        Ignore
                    </button>
                </div>
            </div>
        </div>
    );
}
