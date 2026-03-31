export type AppThemeMode = "light" | "dark";

export const palette = {
  light: {
    background: "#FFFFFF",
    surface: "#F7F7F7",
    surface2: "#EFEFEF",
    card: "#FFFFFF",
    border: "#E3E3E3",
    text: "#111111",
    muted: "#666666",
    primary: "#D71920",
    primarySoft: "#FDEBEC",
    bubbleUser: "#D71920",
    bubbleAssistant: "#F5F5F5",
    white: "#FFFFFF",
    tabBar: "#FFFFFF",
  },
  dark: {
    background: "#111111",
    surface: "#1A1A1A",
    surface2: "#242424",
    card: "#181818",
    border: "#2F2F2F",
    text: "#F5F5F5",
    muted: "#B5B5B5",
    primary: "#E53935",
    primarySoft: "#3A1A1A",
    bubbleUser: "#E53935",
    bubbleAssistant: "#242424",
    white: "#FFFFFF",
    tabBar: "#151515",
  },
};

export const getFontSize = (base: number, largeText: boolean) => {
  return largeText ? base + 2 : base;
};