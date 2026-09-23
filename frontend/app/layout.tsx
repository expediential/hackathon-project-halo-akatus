import type { Metadata } from 'next'
import './globals.css'
import { AppShell } from '../src/components/layout/AppShell'

export const metadata: Metadata = {
  title: 'Emergency Response Intelligence',
  description: 'Evidence-led emergency information management and response support.',
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><AppShell>{children}</AppShell></body></html>
}
