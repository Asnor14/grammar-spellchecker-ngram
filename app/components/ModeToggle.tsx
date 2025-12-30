'use client';

import Icon from './Icon';

interface ModeToggleProps {
    mode: 'bigram' | 'trigram';
    onChange: (mode: 'bigram' | 'trigram') => void;
    disabled?: boolean;
}

export default function ModeToggle({
    mode,
    onChange,
    disabled = false,
}: ModeToggleProps) {
    return (
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4">
            <div className="flex items-center gap-2 text-sm text-[var(--color-text-300)]">
                <Icon name="info" size={14} />
                <span>N-gram Model:</span>
            </div>
            <div className={`toggle-container ${disabled ? 'opacity-50' : ''}`}>
                <button
                    onClick={() => onChange('bigram')}
                    disabled={disabled}
                    className={`toggle-option flex items-center gap-2 ${mode === 'bigram' ? 'active' : ''}`}
                    title="Bigram model (2-word context)"
                >
                    <Icon name="bigram" size={16} />
                    <span>Bigram</span>
                </button>
                <button
                    onClick={() => onChange('trigram')}
                    disabled={disabled}
                    className={`toggle-option flex items-center gap-2 ${mode === 'trigram' ? 'active' : ''}`}
                    title="Trigram model (3-word context)"
                >
                    <Icon name="trigram" size={16} />
                    <span>Trigram</span>
                </button>
            </div>
        </div>
    );
}
