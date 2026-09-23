"use client"

import NextLink from 'next/link'
import type { ComponentProps } from 'react'

type LinkProps = Omit<ComponentProps<typeof NextLink>, 'href'> & { href?: string; to?: string }

export function Link({ href, to, ...props }: LinkProps) {
  return <NextLink href={href ?? to ?? '/'} {...props} />
}
