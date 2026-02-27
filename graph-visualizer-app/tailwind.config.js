module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      width: {
        '72': '19rem',
        '80': '20rem',
        '160': '40rem'
      },
      colors: {
        'custom-primary': '#4E3955',
        'custom-secondary': '#312b33',
        'custom-tertiary': '#b1b2b5',
        'custom-error': '#ff0042',
      }
    }
  },
}
