'use client';

import { useState, useRef, useCallback } from 'react';
import Icon from './Icon';
import { MAX_FILE_SIZE_MB, SUPPORTED_FILE_TYPES } from '@/app/lib/constants';
import { formatFileSize } from '@/app/lib/helpers';

interface FileUploadProps {
    onFileSelect: (file: File) => void;
    selectedFile: File | null;
    onClear: () => void;
    disabled?: boolean;
}

export default function FileUpload({
    onFileSelect,
    selectedFile,
    onClear,
    disabled = false,
}: FileUploadProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const validateFile = useCallback((file: File): string | null => {
        const extension = '.' + file.name.split('.').pop()?.toLowerCase();

        if (!SUPPORTED_FILE_TYPES.includes(extension)) {
            return `Unsupported file type. Please upload ${SUPPORTED_FILE_TYPES.join(' or ')} files.`;
        }

        const fileSizeMB = file.size / (1024 * 1024);
        if (fileSizeMB > MAX_FILE_SIZE_MB) {
            return `File too large. Maximum size is ${MAX_FILE_SIZE_MB}MB.`;
        }

        return null;
    }, []);

    const handleFile = useCallback((file: File) => {
        const validationError = validateFile(file);
        if (validationError) {
            setError(validationError);
            return;
        }

        setError(null);
        onFileSelect(file);
    }, [validateFile, onFileSelect]);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (!disabled) {
            setIsDragging(true);
        }
    }, [disabled]);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        if (disabled) return;

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }, [disabled, handleFile]);

    const handleClick = () => {
        if (!disabled) {
            fileInputRef.current?.click();
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            handleFile(files[0]);
        }
    };

    return (
        <div className="space-y-3">
            <input
                ref={fileInputRef}
                type="file"
                accept={SUPPORTED_FILE_TYPES.join(',')}
                onChange={handleInputChange}
                className="hidden"
                disabled={disabled}
            />

            <div
                onClick={handleClick}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`
          upload-zone min-h-[300px] md:min-h-[400px]
          flex flex-col items-center justify-center gap-4
          ${isDragging ? 'drag-over' : ''}
          ${selectedFile ? 'has-file' : ''}
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
            >
                {selectedFile ? (
                    <>
                        <div className="w-16 h-16 rounded-full bg-[var(--color-bg-700)] flex items-center justify-center">
                            <Icon name="file-check" size={32} className="text-[var(--color-success)]" />
                        </div>
                        <div className="text-center">
                            <p className="text-[var(--color-text-100)] font-semibold text-lg">
                                {selectedFile.name}
                            </p>
                            <p className="text-[var(--color-text-300)] text-sm mt-1">
                                {formatFileSize(selectedFile.size)}
                            </p>
                        </div>
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                onClear();
                            }}
                            disabled={disabled}
                            className="btn btn-secondary text-sm"
                        >
                            <Icon name="trash" size={16} />
                            <span>Remove File</span>
                        </button>
                    </>
                ) : (
                    <>
                        <div className="w-16 h-16 rounded-full bg-[var(--color-bg-700)] flex items-center justify-center">
                            <Icon name="upload" size={32} className="text-[var(--color-text-300)]" />
                        </div>
                        <div className="text-center">
                            <p className="text-[var(--color-text-100)] font-semibold">
                                {isDragging ? 'Drop your file here' : 'Drag & drop a file here'}
                            </p>
                            <p className="text-[var(--color-text-300)] text-sm mt-1">
                                or click to browse
                            </p>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-[var(--color-text-300)]">
                            <Icon name="info" size={14} />
                            <span>Supports {SUPPORTED_FILE_TYPES.join(', ')} (max {MAX_FILE_SIZE_MB}MB)</span>
                        </div>
                    </>
                )}
            </div>

            {error && (
                <div className="flex items-center gap-2 text-[var(--color-error-spelling)] text-sm">
                    <Icon name="alert-circle" size={16} />
                    <span>{error}</span>
                </div>
            )}
        </div>
    );
}
