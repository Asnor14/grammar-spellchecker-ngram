'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import TextInput from './components/TextInput';
import FileUpload from './components/FileUpload';
import InputModeToggle from './components/InputModeToggle';
import ModeToggle from './components/ModeToggle';
import Loading from './components/Loading';
import Icon from './components/Icon';
import { checkText, checkFile } from '@/app/lib/api';
import { AnalysisResult } from '@/app/types/analysis';

export default function Home() {
  const router = useRouter();
  const [inputMode, setInputMode] = useState<'text' | 'file'>('text');
  const [ngramMode, setNgramMode] = useState<'bigram' | 'trigram'>('trigram');
  const [text, setText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleClearText = useCallback(() => {
    setText('');
    setError(null);
  }, []);

  const handleClearFile = useCallback(() => {
    setSelectedFile(null);
    setError(null);
  }, []);

  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file);
    setError(null);
  }, []);

  const canSubmit = inputMode === 'text' ? text.trim().length > 0 : selectedFile !== null;

  const handleSubmit = async () => {
    if (!canSubmit) return;

    setIsLoading(true);
    setError(null);

    try {
      let result: AnalysisResult;

      if (inputMode === 'text') {
        result = await checkText(text, ngramMode);
      } else if (selectedFile) {
        result = await checkFile(selectedFile, ngramMode);
      } else {
        throw new Error('No input provided');
      }

      // Store result in sessionStorage and navigate to results page
      sessionStorage.setItem('grammarAnalysisResult', JSON.stringify(result));
      router.push('/result');
    } catch (err) {
      console.error('Analysis error:', err);
      setError(
        err instanceof Error
          ? err.message
          : 'An error occurred while analyzing your text. Please ensure the backend server is running.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--color-bg-900)]">
      {/* Header */}
      <header className="border-b border-[var(--color-bg-700)]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-semibold text-[var(--color-text-100)]">
                Grammar Checker
              </h1>
              <p className="text-sm sm:text-base text-[var(--color-text-300)] mt-1">
                Academic-grade text analysis using statistical n-gram models
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs text-[var(--color-text-300)] bg-[var(--color-bg-800)] rounded-lg px-3 py-2">
              <Icon name="info" size={14} />
              <span>Powered by Brown & Gutenberg Corpora</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Controls Row */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <InputModeToggle
              mode={inputMode}
              onChange={setInputMode}
              disabled={isLoading}
            />
            <ModeToggle
              mode={ngramMode}
              onChange={setNgramMode}
              disabled={isLoading}
            />
          </div>

          {/* Input Area */}
          <div className="card">
            {inputMode === 'text' ? (
              <TextInput
                value={text}
                onChange={setText}
                onClear={handleClearText}
                disabled={isLoading}
              />
            ) : (
              <FileUpload
                selectedFile={selectedFile}
                onFileSelect={handleFileSelect}
                onClear={handleClearFile}
                disabled={isLoading}
              />
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-start gap-3 p-4 bg-[rgba(155,68,68,0.1)] border border-[var(--color-error-spelling)] rounded-lg">
              <Icon name="alert-circle" size={20} className="text-[var(--color-error-spelling)] flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm text-[var(--color-error-spelling)] font-medium">Error</p>
                <p className="text-sm text-[var(--color-text-300)] mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-center">
            <button
              onClick={handleSubmit}
              disabled={!canSubmit || isLoading}
              className="btn btn-primary text-base py-3 px-8 min-w-[200px]"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-[var(--color-bg-900)] border-t-transparent rounded-full animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Icon name="file-check" size={20} />
                  <span>Check Grammar</span>
                </>
              )}
            </button>
          </div>

          {/* Info Section */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="card-inner text-center p-6">
              <div className="w-12 h-12 rounded-full bg-[var(--color-bg-700)] flex items-center justify-center mx-auto mb-4">
                <Icon name="spell-check" size={24} className="text-[var(--color-error-spelling)]" />
              </div>
              <h3 className="font-semibold text-[var(--color-text-100)] mb-2">Spelling Check</h3>
              <p className="text-sm text-[var(--color-text-300)]">
                Detects misspelled words using dictionary-based matching with edit distance algorithms
              </p>
            </div>
            <div className="card-inner text-center p-6">
              <div className="w-12 h-12 rounded-full bg-[var(--color-bg-700)] flex items-center justify-center mx-auto mb-4">
                <Icon name="book-open" size={24} className="text-[var(--color-error-grammar)]" />
              </div>
              <h3 className="font-semibold text-[var(--color-text-100)] mb-2">Grammar Analysis</h3>
              <p className="text-sm text-[var(--color-text-300)]">
                Statistical n-gram models identify contextually incorrect word usage
              </p>
            </div>
            <div className="card-inner text-center p-6">
              <div className="w-12 h-12 rounded-full bg-[var(--color-bg-700)] flex items-center justify-center mx-auto mb-4">
                <Icon name="type" size={24} className="text-[var(--color-error-punctuation)]" />
              </div>
              <h3 className="font-semibold text-[var(--color-text-100)] mb-2">Punctuation Rules</h3>
              <p className="text-sm text-[var(--color-text-300)]">
                Rule-based detection of missing periods, commas, and capitalization errors
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[var(--color-bg-700)] mt-auto">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-[var(--color-text-300)]">
            Statistical N-gram Language Model • Kneser-Ney Smoothing • Deterministic Analysis
          </p>
        </div>
      </footer>

      {/* Loading Overlay */}
      {isLoading && <Loading fullScreen text="Analyzing your text..." />}
    </div>
  );
}
