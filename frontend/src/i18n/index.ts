import { createContext, useContext } from 'react'
import en from './en'
import tk from './tk'

export type Lang = 'en' | 'tk'
export type TranslationKey = keyof typeof en

const locales: Record<Lang, Record<string, string>> = { en, tk }

export function t(key: TranslationKey, lang: Lang): string {
  return locales[lang]?.[key] ?? locales.en[key] ?? key
}

export interface AppSettings {
  lang: Lang
  theme: 'dark' | 'light'
  setLang: (l: Lang) => void
  setTheme: (t: 'dark' | 'light') => void
}

export const SettingsContext = createContext<AppSettings>({
  lang: 'tk',
  theme: 'dark',
  setLang: () => {},
  setTheme: () => {},
})

export function useSettings() {
  return useContext(SettingsContext)
}

export function useT() {
  const { lang } = useSettings()
  return (key: TranslationKey) => t(key, lang)
}
