'use client';

import Icon from './Icon';

interface ModelTypeToggleProps {
    modelType: 'ngram' | 'transformer';
    onChange: (modelType: 'ngram' | 'transformer') => void;
    disabled?: boolean;
}

export default function ModelTypeToggle({
    modelType,
    onChange,
    disabled = false,
}: ModelTypeToggleProps) {
    return (
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4">
            <div className="flex items-center gap-2 text-sm text-[var(--color-text-300)]">
                <Icon name="cpu" size={14} />
                <span>Model:</span>
            </div>
            <div className={`toggle-container ${disabled ? 'opacity-50' : ''}`}>
                <button
                    onClick={() => onChange('ngram')}
                    disabled={disabled}
                    className={`toggle-option flex items-center gap-2 ${modelType === 'ngram' ? 'active' : ''}`}
                    title="Basic: Statistical N-gram model (Fast, Lightweight)"
                >
                    <Icon name="bar-chart" size={16} />
                    <span>Basic</span>
                </button>
                <button
                    onClick={() => onChange('transformer')}
                    disabled={disabled}
                    className={`toggle-option flex items-center gap-2 ${modelType === 'transformer' ? 'active' : ''}`}
                    title="Advanced: AI-powered Transformer model (T5, More Accurate)"
                >
                    <Icon name="brain" size={16} />
                    <span>Advanced AI</span>
                </button>
            </div>
        </div>
    );
}
