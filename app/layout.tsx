import type { Metadata } from "next";
import { Raleway } from "next/font/google";
import "./globals.css";
import "./styles/theme.css";

const raleway = Raleway({
  variable: "--font-raleway",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Grammar Checker | Academic-Grade Text Analysis",
  description: "A deterministic grammar, spelling, and punctuation checker using statistical n-gram language models. Powered by the Brown and Gutenberg corpora.",
  keywords: ["grammar checker", "spelling checker", "n-gram", "NLP", "text analysis"],
  authors: [{ name: "Grammar Checker Team" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${raleway.variable} font-['Raleway'] antialiased`}>
        {children}
      </body>
    </html>
  );
}
