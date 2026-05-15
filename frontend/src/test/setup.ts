import '@testing-library/jest-dom/vitest'

// AntD's responsive-related code reads window.matchMedia, which jsdom
// doesn't implement. Stub it so antd components render in tests.
if (!window.matchMedia) {
  window.matchMedia = (query: string) =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as MediaQueryList
}
