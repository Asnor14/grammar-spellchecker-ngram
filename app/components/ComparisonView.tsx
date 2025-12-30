'use client';

import { useMemo } from 'react';
import { highlightDifferences, copyToClipboard } from '@/app/lib/helpers';
import Icon from './Icon';
import { useState } from 'react';

interface ComparisonViewProps {
    original: string;
    corrected: string;
    layout?: 'side-by-side' | 'stacked';
}

export default function ComparisonView({
    original,
    corrected,
    layout = 'stacked',
}: ComparisonViewProps) {
    const [copied, setCopied] = useState(false);
    const { originalParts, correctedParts } = useMemo(
        () => highlightDifferences(original, corrected),
        [original, corrected]
    );

    const hasChanges = original !== corrected;

    const handleCopy = async () => {
        await copyToClipboard(corrected);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="card space-y-4">
            <div className="flex items-center justify-between">
                <h4 className="text-lg font-semibold text-[var(--color-text-100)]">
                    Before & After
                </h4>
                <button
                    onClick={handleCopy}
                    className="btn btn-secondary text-sm"
                    disabled={!hasChanges}
                >
                    <Icon name={copied ? 'check-circle' : 'copy'} size={16} />
                    <span>{copied ? 'Copied!' : 'Copy Corrected'}</span>
                </button>
            </div>

            {!hasChanges ? (
                <div className="text-center py-6 text-[var(--color-text-300)]">
                    <Icon name="check-circle" size={32} className="mx-auto mb-2 text-[var(--color-success)]" />
                    <p>No corrections needed. Original text is grammatically correct.</p>
                </div>
            ) : (
                <div
                    className={`
            ${layout === 'side-by-side'
                            ? 'grid grid-cols-1 md:grid-cols-2 gap-4'
                            : 'space-y-4'
                        }
          `}
                >
                    {/* Original */}
                    <div className="comparison-panel">
                        <div className="comparison-label flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-[var(--color-error-spelling)]" />
                            Original
                        </div>
                        <div className="text-[var(--color-text-100)] leading-relaxed whitespace-pre-wrap">
                            {originalParts.map((part, index) => (
                                <span
                                    key={index}
                                    className={part.changed ? 'text-removed' : ''}
                                >
                                    {part.text}
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Corrected */}
                    <div className="comparison-panel">
                        <div className="comparison-label flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-[var(--color-success)]" />
                            Corrected
                        </div>
                        <div className="text-[var(--color-text-100)] leading-relaxed whitespace-pre-wrap">
                            {correctedParts.map((part, index) => (
                                <span
                                    key={index}
                                    className={part.changed ? 'text-changed' : ''}
                                >
                                    {part.text}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
