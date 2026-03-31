import React from "react";
import { SafeAreaView, StyleSheet, Switch, Text, View } from "react-native";
import { getFontSize, palette } from "../../src/constants/theme";
import { useAppSettings } from "../../src/context/AppSettingsContext";

export default function SettingsScreen() {
  const { themeMode, largeText, setThemeMode, setLargeText } = useAppSettings();
  const colors = palette[themeMode];

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.background }]}>
      <View style={styles.container}>
        <Text
          style={[
            styles.title,
            {
              color: colors.text,
              fontSize: getFontSize(28, largeText),
            },
          ]}
        >
          Settings
        </Text>

        <View
          style={[
            styles.card,
            {
              backgroundColor: colors.card,
              borderColor: colors.border,
            },
          ]}
        >
          <Text
            style={[
              styles.cardTitle,
              {
                color: colors.text,
                fontSize: getFontSize(17, largeText),
              },
            ]}
          >
            Dark Mode
          </Text>
          <Text
            style={[
              styles.cardText,
              {
                color: colors.muted,
                fontSize: getFontSize(14, largeText),
              },
            ]}
          >
            Switch between light and dark appearance.
          </Text>
          <Switch
            value={themeMode === "dark"}
            onValueChange={(value) => setThemeMode(value ? "dark" : "light")}
          />
        </View>

        <View
          style={[
            styles.card,
            {
              backgroundColor: colors.card,
              borderColor: colors.border,
            },
          ]}
        >
          <Text
            style={[
              styles.cardTitle,
              {
                color: colors.text,
                fontSize: getFontSize(17, largeText),
              },
            ]}
          >
            Large Text
          </Text>
          <Text
            style={[
              styles.cardText,
              {
                color: colors.muted,
                fontSize: getFontSize(14, largeText),
              },
            ]}
          >
            Increase font size across the app for readability.
          </Text>
          <Switch value={largeText} onValueChange={setLargeText} />
        </View>

        <View
          style={[
            styles.card,
            {
              backgroundColor: colors.card,
              borderColor: colors.border,
            },
          ]}
        >
          <Text
            style={[
              styles.cardTitle,
              {
                color: colors.text,
                fontSize: getFontSize(17, largeText),
              },
            ]}
          >
            About Campus AI
          </Text>
          <Text
            style={[
              styles.cardText,
              {
                color: colors.muted,
                fontSize: getFontSize(14, largeText),
              },
            ]}
          >
            This interface is designed for a chatbot-first campus assistant that can support telemetry, database, PDF, and official-campus information workflows. :contentReference[oaicite:3]{index=3}
          </Text>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
  },
  container: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 18,
    paddingBottom: 20,
  },
  title: {
    fontWeight: "900",
    marginBottom: 20,
  },
  card: {
    borderRadius: 22,
    borderWidth: 1,
    padding: 18,
    marginBottom: 14,
  },
  cardTitle: {
    fontWeight: "800",
    marginBottom: 8,
  },
  cardText: {
    lineHeight: 22,
    marginBottom: 14,
  },
});