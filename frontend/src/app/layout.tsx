import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VLab-ERP: Virtual Lab & Business Simulation Platform",
  description: "Platform simulasi modular ERP terpadu untuk pembelajaran mahasiswa",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id">
      <body className="antialiased min-h-screen flex flex-col bg-slate-100 text-slate-900">
        {children}
      </body>
    </html>
  );
}
