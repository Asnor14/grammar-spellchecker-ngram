'use client';

import { useMemo } from 'react';
import { GrammarError, ErrorStats } from '@/app/types/analysis';
import { calculateErrorStats } from '@/app/lib/helpers';
import { ERROR_TYPE_LABELS } from '@/app/lib/constants';
import Icon from './Icon';

interface ErrorSummaryProps {
    errors: GrammarError[];
    onErrorClick?: (error: GrammarError) => void;
}

export default function ErrorSummary({
    errors,
    onErrorClick,
}: ErrorSummaryProps) {
    const stats = useMemo(() => calculateErrorStats(errors), [errors]);

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

    if (errors.length === 0) {
        return (
            <div className="card">
                <div className="flex flex-col items-center justify-center py-8 text-center">
                    <div className="w-16 h-16 rounded-full bg-[var(--color-bg-800)] flex items-center justify-center mb-4">
                        <Icon name="check-circle" size={32} className="text-[var(--color-success)]" />
                    </div>
                    <h4 className="text-lg font-semibold text-[var(--color-text-100)] mb-2">
                        No Errors Found
                    </h4>
                    <p className="text-sm text-[var(--color-text-300)]">
                        Your text appears to be grammatically correct!
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="card space-y-4">
            <div className="flex items-center justify-between">
                <h4 className="text-lg font-semibold text-[var(--color-text-100)]">
                    Error Summary
                </h4>
                <span className="text-sm text-[var(--color-text-300)]">
                    {stats.total} issue{stats.total !== 1 ? 's' : ''} found
                </span>
            </div>

            {/* Stats badges */}
            <div className="flex flex-wrap gap-2">
                {stats.spelling > 0 && (
                    <div className="error-badge spelling">
                        <Icon name="spell-check" size={12} />
                        <span>{stats.spelling} Spelling</span>
                    </div>
                )}
                {stats.grammar > 0 && (
                    <div className="error-badge grammar">
                        <Icon name="book-open" size={12} />
                        <span>{stats.grammar} Grammar</span>
                    </div>
                )}
                {stats.punctuation > 0 && (
                    <div className="error-badge punctuation">
                        <Icon name="type" size={12} />
                        <span>{stats.punctuation} Punctuation</span>
                    </div>
                )}
            </div>

            {/* Error list */}
            <div className="space-y-2 max-h-[300px] overflow-y-auto">
                {errors.map((error, index) => (
                    <button
                        key={`${error.position.start}-${error.position.end}-${index}`}
                        onClick={() => onErrorClick?.(error)}
                        className="w-full text-left p-3 bg-[var(--color-bg-800)] rounded-lg hover:bg-[var(--color-bg-600)] transition-colors group"
                    >
                        <div className="flex items-start gap-3">
                            <div className={`error-badge ${error.type} mt-0.5`}>
                                <Icon name={getIconName(error.type)} size={12} />
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 flex-wrap">
                                    <span className="text-[var(--color-error-spelling)] line-through text-sm">
                                        {error.original}
                                    </span>
                                    <Icon name="chevron-right" size={12} className="text-[var(--color-text-300)]" />
                                    <span className="text-[var(--color-success)] font-medium text-sm">
                                        {error.suggestion}
                                    </span>
                                </div>
                                <p className="text-xs text-[var(--color-text-300)] mt-1 truncate">
                                    {error.explanation}
                                </p>
                            </div>
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
}
