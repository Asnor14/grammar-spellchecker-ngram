'use client';

import {
    Upload,
    FileCheck,
    Trash2,
    Info,
    Copy,
    Grid2X2,
    Grid3X3,
    ChevronLeft,
    ChevronRight,
    AlertCircle,
    CheckCircle,
    XCircle,
    Loader2,
    FileText,
    SpellCheck,
    BookOpen,
    Type,
    Download,
    RefreshCw,
    Eye,
    EyeOff,
} from 'lucide-react';

export type IconName =
    | 'upload'
    | 'file-check'
    | 'trash'
    | 'info'
    | 'copy'
    | 'bigram'
    | 'trigram'
    | 'chevron-left'
    | 'chevron-right'
    | 'alert-circle'
    | 'check-circle'
    | 'x-circle'
    | 'loader'
    | 'file-text'
    | 'spell-check'
    | 'book-open'
    | 'type'
    | 'download'
    | 'refresh'
    | 'eye'
    | 'eye-off';

interface IconProps {
    name: IconName;
    size?: number;
    className?: string;
    strokeWidth?: number;
    color?: string;
    style?: React.CSSProperties;
}

const iconMap = {
    'upload': Upload,
    'file-check': FileCheck,
    'trash': Trash2,
    'info': Info,
    'copy': Copy,
    'bigram': Grid2X2,
    'trigram': Grid3X3,
    'chevron-left': ChevronLeft,
    'chevron-right': ChevronRight,
    'alert-circle': AlertCircle,
    'check-circle': CheckCircle,
    'x-circle': XCircle,
    'loader': Loader2,
    'file-text': FileText,
    'spell-check': SpellCheck,
    'book-open': BookOpen,
    'type': Type,
    'download': Download,
    'refresh': RefreshCw,
    'eye': Eye,
    'eye-off': EyeOff,
};

export default function Icon({
    name,
    size = 20,
    className = '',
    strokeWidth = 2,
    color,
    style,
}: IconProps) {
    const IconComponent = iconMap[name];

    if (!IconComponent) {
        console.warn(`Icon "${name}" not found`);
        return null;
    }

    return (
        <IconComponent
            size={size}
            className={className}
            strokeWidth={strokeWidth}
            color={color}
            style={style}
        />
    );
}

