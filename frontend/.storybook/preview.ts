import type { Preview } from "@storybook/react-vite";
import "../src/styles/tailwind.css";
import i18n from "../src/locales";

void i18n.changeLanguage("fr");

const preview: Preview = {
  parameters: {
    a11y: {
      test: { include: [/^.*$/] },
    },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    backgrounds: {
      default: "background",
      values: [
        { name: "background", value: "#F8FAFC" },
        { name: "surface", value: "#FFFFFF" },
        { name: "primary-900", value: "#0F172A" },
      ],
    },
    layout: "centered",
    options: {
      storySort: {
        order: ["ui", "shared"],
      },
    },
  },
};

export default preview;
