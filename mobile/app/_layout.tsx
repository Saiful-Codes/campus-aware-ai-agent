import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { AppSettingsProvider, useAppSettings } from "../src/context/AppSettingsContext";

function LayoutContent() {
  const { themeMode } = useAppSettings();

  return (
    <>
      <StatusBar style={themeMode === "light" ? "dark" : "light"} />
      <Stack screenOptions={{ headerShown: false }} />
    </>
  );
}

export default function RootLayout() {
  return (
    <AppSettingsProvider>
      <LayoutContent />
    </AppSettingsProvider>
  );
}
