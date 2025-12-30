'use client';

interface LoadingProps {
    text?: string;
    fullScreen?: boolean;
}

export default function Loading({ text = 'Analyzing...', fullScreen = false }: LoadingProps) {
    const content = (
        <div className="flex flex-col items-center justify-center gap-4">
            <div className="loading-spinner" />
            {text && (
                <p className="text-[var(--color-text-300)] text-sm animate-pulse">
                    {text}
                </p>
            )}
        </div>
    );

    if (fullScreen) {
        return (
            <div className="fixed inset-0 bg-[var(--color-bg-900)]/80 backdrop-blur-sm flex items-center justify-center z-50">
                {content}
            </div>
        );
    }

    return (
        <div className="flex items-center justify-center py-12">
            {content}
        </div>
    );
}

export function LoadingSkeleton({ lines = 3 }: { lines?: number }) {
    return (
        <div className="space-y-3">
            {Array.from({ length: lines }).map((_, i) => (
                <div
                    key={i}
                    className="loading-skeleton h-4"
                    style={{ width: `${Math.random() * 40 + 60}%` }}
                />
            ))}
        </div>
    );
}
