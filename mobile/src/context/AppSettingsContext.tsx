import AsyncStorage from "@react-native-async-storage/async-storage";
import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { AppThemeMode } from "../constants/theme";

type AppSettingsContextType = {
  themeMode: AppThemeMode;
  largeText: boolean;
  setThemeMode: (mode: AppThemeMode) => void;
  setLargeText: (value: boolean) => void;
};

const AppSettingsContext = createContext<AppSettingsContextType | undefined>(undefined);

const THEME_KEY = "campus_ai_theme_mode";
const LARGE_TEXT_KEY = "campus_ai_large_text";

export function AppSettingsProvider({ children }: { children: React.ReactNode }) {
  const [themeMode, setThemeModeState] = useState<AppThemeMode>("light");
  const [largeText, setLargeTextState] = useState(false);

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const savedTheme = await AsyncStorage.getItem(THEME_KEY);
        const savedLargeText = await AsyncStorage.getItem(LARGE_TEXT_KEY);

        if (savedTheme === "light" || savedTheme === "dark") {
          setThemeModeState(savedTheme);
        }

        if (savedLargeText !== null) {
          setLargeTextState(savedLargeText === "true");
        }
      } catch (error) {
        console.log("Failed to load app settings", error);
      }
    };

    loadSettings();
  }, []);

  const setThemeMode = async (mode: AppThemeMode) => {
    setThemeModeState(mode);
    try {
      await AsyncStorage.setItem(THEME_KEY, mode);
    } catch (error) {
      console.log("Failed to save theme mode", error);
    }
  };

  const setLargeText = async (value: boolean) => {
    setLargeTextState(value);
    try {
      await AsyncStorage.setItem(LARGE_TEXT_KEY, String(value));
    } catch (error) {
      console.log("Failed to save large text setting", error);
    }
  };

  const value = useMemo(
    () => ({
      themeMode,
      largeText,
      setThemeMode,
      setLargeText,
    }),
    [themeMode, largeText]
  );

  return <AppSettingsContext.Provider value={value}>{children}</AppSettingsContext.Provider>;
}

export function useAppSettings() {
  const context = useContext(AppSettingsContext);

  if (!context) {
    throw new Error("useAppSettings must be used within AppSettingsProvider");
  }

  return context;
}