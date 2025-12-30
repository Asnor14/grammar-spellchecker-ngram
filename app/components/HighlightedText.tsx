'use client';

import { useState, useCallback, useMemo } from 'react';
import { GrammarError } from '@/app/types/analysis';
import ErrorTooltip from './ErrorTooltip';

interface HighlightedTextProps {
    text: string;
    errors: GrammarError[];
    onApplyFix: (error: GrammarError) => void;
}

interface TextSegment {
    text: string;
    error: GrammarError | null;
    start: number;
    end: number;
}

export default function HighlightedText({
    text,
    errors,
    onApplyFix,
}: HighlightedTextProps) {
    const [activeError, setActiveError] = useState<GrammarError | null>(null);
    const [tooltipPosition, setTooltipPosition] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

    const segments = useMemo((): TextSegment[] => {
        if (errors.length === 0) {
            return [{ text, error: null, start: 0, end: text.length }];
        }

        const sortedErrors = [...errors].sort((a, b) => a.position.start - b.position.start);
        const result: TextSegment[] = [];
        let currentIndex = 0;

        for (const error of sortedErrors) {
            if (error.position.start > currentIndex) {
                result.push({
                    text: text.slice(currentIndex, error.position.start),
                    error: null,
                    start: currentIndex,
                    end: error.position.start,
                });
            }

            result.push({
                text: text.slice(error.position.start, error.position.end),
                error,
                start: error.position.start,
                end: error.position.end,
            });

            currentIndex = error.position.end;
        }

        if (currentIndex < text.length) {
            result.push({
                text: text.slice(currentIndex),
                error: null,
                start: currentIndex,
                end: text.length,
            });
        }

        return result;
    }, [text, errors]);

    const handleErrorClick = useCallback((error: GrammarError, event: React.MouseEvent) => {
        const rect = (event.target as HTMLElement).getBoundingClientRect();
        setTooltipPosition({
            x: rect.left,
            y: rect.bottom + 8,
        });
        setActiveError(error);
    }, []);

    const handleCloseTooltip = useCallback(() => {
        setActiveError(null);
    }, []);

    const handleApplyFix = useCallback((error: GrammarError) => {
        onApplyFix(error);
        setActiveError(null);
    }, [onApplyFix]);

    const getErrorClass = (type: string): string => {
        switch (type) {
            case 'spelling':
                return 'error-spelling';
            case 'grammar':
                return 'error-grammar';
            case 'punctuation':
                return 'error-punctuation';
            default:
                return '';
        }
    };

    return (
        <div className="relative">
            <div className="bg-[var(--color-bg-800)] rounded-xl p-4 md:p-6 min-h-[200px] text-[var(--color-text-100)] leading-relaxed whitespace-pre-wrap break-words">
                {segments.map((segment, index) => {
                    if (segment.error) {
                        return (
                            <span
                                key={`${segment.start}-${segment.end}`}
                                className={`${getErrorClass(segment.error.type)} cursor-pointer transition-opacity hover:opacity-80`}
                                onClick={(e) => handleErrorClick(segment.error!, e)}
                                role="button"
                                tabIndex={0}
                                aria-label={`${segment.error.type} error: ${segment.text}. Suggested correction: ${segment.error.suggestion}`}
                            >
                                {segment.text}
                            </span>
                        );
                    }
                    return <span key={`${segment.start}-${segment.end}`}>{segment.text}</span>;
                })}
            </div>

            {activeError && (
                <ErrorTooltip
                    error={activeError}
                    position={tooltipPosition}
                    onClose={handleCloseTooltip}
                    onApplyFix={handleApplyFix}
                />
            )}
        </div>
    );
}
