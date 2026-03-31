import React from "react";
import { SafeAreaView, StyleSheet, Text, View } from "react-native";
import { getFontSize, palette } from "../../src/constants/theme";
import { useAppSettings } from "../../src/context/AppSettingsContext";

export default function ProfileScreen() {
  const { themeMode, largeText } = useAppSettings();
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
          Profile
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
                fontSize: getFontSize(18, largeText),
              },
            ]}
          >
            Coming soon
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
            This screen is intentionally empty for now and can later hold user profile or account features.
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
  },
  title: {
    fontWeight: "900",
    marginBottom: 20,
  },
  card: {
    borderRadius: 22,
    borderWidth: 1,
    padding: 18,
  },
  cardTitle: {
    fontWeight: "800",
    marginBottom: 8,
  },
  cardText: {
    lineHeight: 22,
  },
});