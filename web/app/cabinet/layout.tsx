import type { Metadata } from "next";
import "./cabinet.css";

export const metadata: Metadata = {
  robots: {
    index: false,
    follow: false,
    nocache: true,
  },
};

export default function CabinetLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return children;
}
