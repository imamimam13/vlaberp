/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        odoo: {
          purple: "#714B67",
          dark: "#017E84",
          light: "#F8F9FA",
          accent: "#00A09D",
          coral: "#E06F6F",
        }
      }
    },
  },
  plugins: [],
};
