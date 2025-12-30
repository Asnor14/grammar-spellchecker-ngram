'use client';

import { SentenceAnalysis } from '@/app/types/analysis';
import Icon from './Icon';

interface SentenceNavigatorProps {
    sentences: SentenceAnalysis[];
    currentIndex: number;
    onChange: (index: number) => void;
}

export default function SentenceNavigator({
    sentences,
    currentIndex,
    onChange,
}: SentenceNavigatorProps) {
    if (sentences.length <= 1) {
        return null;
    }

    const currentSentence = sentences[currentIndex];
    const hasPrev = currentIndex > 0;
    const hasNext = currentIndex < sentences.length - 1;

    return (
        <div className="sentence-nav">
            <button
                onClick={() => onChange(currentIndex - 1)}
                disabled={!hasPrev}
                className="btn btn-icon btn-ghost disabled:opacity-30"
                aria-label="Previous sentence"
            >
                <Icon name="chevron-left" size={20} />
            </button>

            <div className="flex-1 text-center">
                <span className="text-sm text-[var(--color-text-300)]">
                    Sentence {currentIndex + 1} of {sentences.length}
                </span>
                {currentSentence && (
                    <div className="flex items-center justify-center gap-2 mt-1">
                        <span className="text-xs text-[var(--color-text-300)]">
                            {currentSentence.errors.length} error{currentSentence.errors.length !== 1 ? 's' : ''}
                        </span>
                        <span className="text-xs text-[var(--color-bg-600)]">•</span>
                        <span
                            className="text-xs font-medium"
                            style={{
                                color: currentSentence.fluencyScore >= 80
                                    ? 'var(--color-success)'
                                    : currentSentence.fluencyScore >= 50
                                        ? 'var(--color-warning)'
                                        : 'var(--color-error-spelling)',
                            }}
                        >
                            {Math.round(currentSentence.fluencyScore)}% fluency
                        </span>
                    </div>
                )}
            </div>

            <div className="sentence-indicator hidden md:flex">
                {sentences.map((_, index) => (
                    <button
                        key={index}
                        onClick={() => onChange(index)}
                        className={`sentence-dot ${index === currentIndex ? 'active' : ''}`}
                        aria-label={`Go to sentence ${index + 1}`}
                    />
                ))}
            </div>

            <button
                onClick={() => onChange(currentIndex + 1)}
                disabled={!hasNext}
                className="btn btn-icon btn-ghost disabled:opacity-30"
                aria-label="Next sentence"
            >
                <Icon name="chevron-right" size={20} />
            </button>
        </div>
    );
}
