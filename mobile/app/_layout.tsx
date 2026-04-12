import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import {
  AppSettingsProvider,
  useAppSettings,
} from "../src/context/AppSettingsContext";
import { AuthProvider } from "../src/context/AuthContext"; // ✅ add this

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
    <AuthProvider> {/* ✅ wrap auth FIRST */}
      <AppSettingsProvider>
        <LayoutContent />
      </AppSettingsProvider>
    </AuthProvider>
  );
}
