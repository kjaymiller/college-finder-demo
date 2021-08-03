module.exports = {
  purge: {
    enabled: true,
    mode: 'all',
    content: [
      './templates/**/*.html',
    ],
  },
  theme: {
    extend: {},
  },
  variants: {},
  plugins: [
    // ...
    require('tailwindcss'),
    require('autoprefixer'),
    // ...
  ],
}
