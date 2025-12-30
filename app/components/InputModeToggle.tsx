'use client';

import Icon from './Icon';

interface InputModeToggleProps {
    mode: 'text' | 'file';
    onChange: (mode: 'text' | 'file') => void;
    disabled?: boolean;
}

export default function InputModeToggle({
    mode,
    onChange,
    disabled = false,
}: InputModeToggleProps) {
    return (
        <div className={`toggle-container ${disabled ? 'opacity-50' : ''}`}>
            <button
                onClick={() => onChange('text')}
                disabled={disabled}
                className={`toggle-option ${mode === 'text' ? 'active' : ''}`}
            >
                <Icon name="file-text" size={16} />
                <span className="ml-2">Text Input</span>
            </button>
            <button
                onClick={() => onChange('file')}
                disabled={disabled}
                className={`toggle-option ${mode === 'file' ? 'active' : ''}`}
            >
                <Icon name="upload" size={16} />
                <span className="ml-2">File Upload</span>
            </button>
        </div>
    );
}
