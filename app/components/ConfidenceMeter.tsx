'use client';

import { useMemo } from 'react';
import { getConfidenceLevel, formatConfidenceScore } from '@/app/lib/helpers';

interface ConfidenceMeterProps {
    score: number;
    size?: 'sm' | 'md' | 'lg';
    showLabel?: boolean;
}

export default function ConfidenceMeter({
    score,
    size = 'md',
    showLabel = true,
}: ConfidenceMeterProps) {
    const { label, color } = useMemo(() => getConfidenceLevel(score), [score]);

    const dimensions = {
        sm: { size: 80, strokeWidth: 6, fontSize: 'text-lg' },
        md: { size: 120, strokeWidth: 8, fontSize: 'text-2xl' },
        lg: { size: 160, strokeWidth: 10, fontSize: 'text-3xl' },
    };

    const { size: svgSize, strokeWidth, fontSize } = dimensions[size];
    const radius = (svgSize - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (score / 100) * circumference;

    return (
        <div className="flex flex-col items-center gap-2">
            <div className="meter-circular" style={{ width: svgSize, height: svgSize }}>
                <svg width={svgSize} height={svgSize}>
                    {/* Background circle */}
                    <circle
                        cx={svgSize / 2}
                        cy={svgSize / 2}
                        r={radius}
                        fill="none"
                        stroke="var(--color-bg-700)"
                        strokeWidth={strokeWidth}
                    />
                    {/* Progress circle */}
                    <circle
                        cx={svgSize / 2}
                        cy={svgSize / 2}
                        r={radius}
                        fill="none"
                        stroke={color}
                        strokeWidth={strokeWidth}
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        strokeDashoffset={strokeDashoffset}
                        style={{
                            transition: 'stroke-dashoffset 0.8s ease-out',
                        }}
                    />
                </svg>
                <span
                    className={`meter-circular-value ${fontSize} font-semibold`}
                    style={{ color }}
                >
                    {formatConfidenceScore(score)}
                </span>
            </div>
            {showLabel && (
                <div className="text-center">
                    <p className="text-sm font-medium" style={{ color }}>
                        {label}
                    </p>
                    <p className="text-xs text-[var(--color-text-300)]">
                        Grammar Confidence
                    </p>
                </div>
            )}
        </div>
    );
}

export function ConfidenceBar({ score }: { score: number }) {
    const { label, color } = useMemo(() => getConfidenceLevel(score), [score]);

    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between">
                <span className="text-sm text-[var(--color-text-300)]">Grammar Confidence</span>
                <span className="text-sm font-semibold" style={{ color }}>
                    {formatConfidenceScore(score)}
                </span>
            </div>
            <div className="meter-container">
                <div
                    className="meter-fill"
                    style={{
                        width: `${score}%`,
                        backgroundColor: color,
                    }}
                />
            </div>
            <p className="text-xs text-center" style={{ color }}>
                {label}
            </p>
        </div>
    );
}
