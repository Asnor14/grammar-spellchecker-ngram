'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { AnalysisResult, GrammarError } from '@/app/types/analysis';
import HighlightedText from '@/app/components/HighlightedText';
import ErrorSummary from '@/app/components/ErrorSummary';
import ConfidenceMeter from '@/app/components/ConfidenceMeter';
import SentenceNavigator from '@/app/components/SentenceNavigator';
import ComparisonView from '@/app/components/ComparisonView';
import Loading from '@/app/components/Loading';
import Icon from '@/app/components/Icon';

export default function ResultPage() {
    const router = useRouter();
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [currentSentenceIndex, setCurrentSentenceIndex] = useState(0);
    const [displayText, setDisplayText] = useState('');
    const [displayErrors, setDisplayErrors] = useState<GrammarError[]>([]);

    useEffect(() => {
        const storedResult = sessionStorage.getItem('grammarAnalysisResult');
        if (storedResult) {
            try {
                const parsed: AnalysisResult = JSON.parse(storedResult);
                setResult(parsed);
                setDisplayText(parsed.originalText);
                setDisplayErrors(parsed.errors);
            } catch (e) {
                console.error('Failed to parse result:', e);
                router.push('/');
            }
        } else {
            router.push('/');
        }
    }, [router]);

    const handleApplyFix = useCallback((error: GrammarError) => {
        if (!result) return;

        // Apply the fix to the display text
        const before = displayText.slice(0, error.position.start);
        const after = displayText.slice(error.position.end);
        const newText = before + error.suggestion + after;

        // Calculate position offset
        const offset = error.suggestion.length - error.original.length;

        // Update errors to remove the fixed one and adjust positions of subsequent errors
        const updatedErrors = displayErrors
            .filter((e) => e !== error)
            .map((e) => {
                if (e.position.start > error.position.start) {
                    return {
                        ...e,
                        position: {
                            start: e.position.start + offset,
                            end: e.position.end + offset,
                        },
                    };
                }
                return e;
            });

        setDisplayText(newText);
        setDisplayErrors(updatedErrors);
    }, [displayText, displayErrors, result]);

    const handleApplyAllFixes = useCallback(() => {
        if (!result) return;
        setDisplayText(result.correctedText);
        setDisplayErrors([]);
    }, [result]);

    const handleReset = useCallback(() => {
        if (!result) return;
        setDisplayText(result.originalText);
        setDisplayErrors(result.errors);
    }, [result]);

    const handleNewCheck = useCallback(() => {
        sessionStorage.removeItem('grammarAnalysisResult');
        router.push('/');
    }, [router]);

    if (!result) {
        return <Loading fullScreen text="Loading results..." />;
    }

    const hasAppliedFixes = displayText !== result.originalText;
    const allFixesApplied = displayErrors.length === 0 && result.errors.length > 0;

    return (
        <div className="min-h-screen bg-[var(--color-bg-900)]">
            {/* Header */}
            <header className="border-b border-[var(--color-bg-700)]">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                        <div className="flex items-center gap-4">
                            <button
                                onClick={handleNewCheck}
                                className="btn btn-ghost"
                            >
                                <Icon name="chevron-left" size={20} />
                                <span className="hidden sm:inline">Back</span>
                            </button>
                            <div>
                                <h1 className="text-xl sm:text-2xl font-semibold text-[var(--color-text-100)]">
                                    Analysis Results
                                </h1>
                                <p className="text-sm text-[var(--color-text-300)]">
                                    {result.ngramMode === 'trigram' ? 'Trigram' : 'Bigram'} analysis •
                                    {result.processingTimeMs ? ` ${result.processingTimeMs}ms` : ' Complete'}
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            {hasAppliedFixes && (
                                <button
                                    onClick={handleReset}
                                    className="btn btn-secondary text-sm"
                                >
                                    <Icon name="refresh" size={16} />
                                    <span>Reset</span>
                                </button>
                            )}
                            {displayErrors.length > 0 && (
                                <button
                                    onClick={handleApplyAllFixes}
                                    className="btn btn-primary text-sm"
                                >
                                    <Icon name="check-circle" size={16} />
                                    <span>Apply All Fixes</span>
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Column - Main Content */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Sentence Navigator */}
                        {result.sentences.length > 1 && (
                            <SentenceNavigator
                                sentences={result.sentences}
                                currentIndex={currentSentenceIndex}
                                onChange={setCurrentSentenceIndex}
                            />
                        )}

                        {/* Highlighted Text */}
                        <div className="card">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-[var(--color-text-100)]">
                                    Your Text
                                </h3>
                                {allFixesApplied && (
                                    <div className="flex items-center gap-2 text-sm text-[var(--color-success)]">
                                        <Icon name="check-circle" size={16} />
                                        <span>All fixes applied</span>
                                    </div>
                                )}
                            </div>
                            <HighlightedText
                                text={displayText}
                                errors={displayErrors}
                                onApplyFix={handleApplyFix}
                            />
                            <p className="text-xs text-[var(--color-text-300)] mt-3">
                                Click on any underlined word to see correction suggestions
                            </p>
                        </div>

                        {/* Comparison View */}
                        <ComparisonView
                            original={result.originalText}
                            corrected={displayErrors.length === 0 ? displayText : result.correctedText}
                            layout="stacked"
                        />
                    </div>

                    {/* Right Column - Sidebar */}
                    <div className="space-y-6">
                        {/* Confidence Score */}
                        <div className="card flex flex-col items-center py-6">
                            <ConfidenceMeter
                                score={result.confidenceScore}
                                size="lg"
                                showLabel={true}
                            />
                        </div>

                        {/* Error Summary */}
                        <ErrorSummary
                            errors={displayErrors}
                            onErrorClick={(error) => {
                                // Could scroll to error or highlight it
                                console.log('Error clicked:', error);
                            }}
                        />

                        {/* Analysis Info */}
                        <div className="card">
                            <h4 className="text-sm font-semibold text-[var(--color-text-100)] mb-3">
                                Analysis Details
                            </h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-[var(--color-text-300)]">Model</span>
                                    <span className="text-[var(--color-text-100)] font-medium">
                                        {result.ngramMode === 'trigram' ? 'Trigram (3-gram)' : 'Bigram (2-gram)'}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[var(--color-text-300)]">Sentences</span>
                                    <span className="text-[var(--color-text-100)] font-medium">
                                        {result.sentences.length}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[var(--color-text-300)]">Total Errors</span>
                                    <span className="text-[var(--color-text-100)] font-medium">
                                        {result.errors.length}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[var(--color-text-300)]">Processing Time</span>
                                    <span className="text-[var(--color-text-100)] font-medium">
                                        {result.processingTimeMs || 'N/A'}ms
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* New Check Button */}
                        <button
                            onClick={handleNewCheck}
                            className="btn btn-secondary w-full py-3"
                        >
                            <Icon name="refresh" size={18} />
                            <span>Check Another Text</span>
                        </button>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="border-t border-[var(--color-bg-700)] mt-auto">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <p className="text-center text-xs text-[var(--color-text-300)]">
                        Results generated using Kneser-Ney smoothed interpolated n-gram model
                    </p>
                </div>
            </footer>
        </div>
    );
}
