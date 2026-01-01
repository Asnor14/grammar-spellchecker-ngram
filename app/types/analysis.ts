export interface GrammarError {
  type: 'spelling' | 'grammar' | 'punctuation' | 'ngram' | 'semantic' | 'structure' | 'ai';
  position: {
    start: number;
    end: number;
  };
  original: string;
  suggestion: string;
  explanation: string;
  sentenceIndex: number;
}

export interface SentenceAnalysis {
  index: number;
  original: string;
  corrected: string;
  errors: GrammarError[];
  fluencyScore: number;
}

export interface AnalysisResult {
  originalText: string;
  correctedText: string;
  errors: GrammarError[];
  confidenceScore: number;
  sentences: SentenceAnalysis[];
  ngramMode: 'bigram' | 'trigram' | '4gram' | 'Transformer-AI';
  processingTimeMs: number;
}

export interface CheckTextRequest {
  text: string;
  ngram: 'bigram' | 'trigram' | '4gram';
  model_type?: 'ngram' | 'transformer';
}

export interface CheckFileRequest {
  file: File;
  ngram: 'bigram' | 'trigram' | '4gram';
  model_type?: 'ngram' | 'transformer';
}

export type ErrorType = 'spelling' | 'grammar' | 'punctuation' | 'ngram' | 'semantic' | 'structure' | 'ai';

export interface ErrorStats {
  spelling: number;
  grammar: number;
  punctuation: number;
  ngram: number;
  semantic: number;
  structure: number;
  ai: number;
  total: number;
}
