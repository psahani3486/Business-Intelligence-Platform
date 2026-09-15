import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import QueryProvider from "@/components/QueryProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Pulse BI - E-Commerce Analytics Platform",
  description: "Retail analytics, forecasting, and customer intelligence platform built on Olist dataset",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1.0,
  maximumScale: 1.0,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryProvider>
          <div className="app-container">
            <Sidebar />
            <div className="main-content">
              <Header />
              {children}
            </div>
          </div>
        </QueryProvider>
      </body>
    </html>
  );
}
