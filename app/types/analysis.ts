export interface GrammarError {
  type: 'spelling' | 'grammar' | 'punctuation';
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
  ngramMode: 'bigram' | 'trigram' | '4gram';
  processingTimeMs: number;
}

export interface CheckTextRequest {
  text: string;
  ngram: 'bigram' | 'trigram' | '4gram';
}

export interface CheckFileRequest {
  file: File;
  ngram: 'bigram' | 'trigram' | '4gram';
}

export type ErrorType = 'spelling' | 'grammar' | 'punctuation';

export interface ErrorStats {
  spelling: number;
  grammar: number;
  punctuation: number;
  total: number;
}
