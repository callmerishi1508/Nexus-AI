import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import { GeistSans } from "geist/font/sans";
import "./globals.css";

const jetbrains = JetBrains_Mono({ 
  subsets: ["latin"], 
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "NEXUS Command Center",
  description: "Autonomous Competitive Intelligence Infrastructure",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${GeistSans.variable} ${jetbrains.variable} dark`}>
      <body className="font-sans antialiased text-zinc-300 min-h-screen bg-[#09090b] selection:bg-indigo-500/30 selection:text-white relative">
        {/* Restrained Base Grid */}
        <div className="pointer-events-none fixed inset-0 z-0 bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:32px_32px] [mask-image:radial-gradient(ellipse_100%_100%_at_50%_0%,#000_10%,transparent_100%)]"></div>
        
        {/* Main Content */}
        <div className="relative z-20 h-screen flex flex-col">
          {children}
        </div>
      </body>
    </html>
  );
}
