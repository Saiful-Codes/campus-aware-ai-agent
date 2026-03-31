import { router } from "expo-router";
import React from "react";
import { Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";
import { getFontSize, palette } from "../../src/constants/theme";
import { useAppSettings } from "../../src/context/AppSettingsContext";

export default function HomeScreen() {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.background }]}>
      <View style={styles.container}>
        <View style={styles.heroSection}>
          <View
            style={[
              styles.logoCircle,
              {
                backgroundColor: colors.primarySoft,
                borderColor: colors.primary,
              },
            ]}
          >
            <Text style={[styles.logoText, { color: colors.primary }]}>CAI</Text>
          </View>

          <Text
            style={[
              styles.brandTitle,
              {
                color: colors.text,
                fontSize: getFontSize(34, largeText),
              },
            ]}
          >
            Campus AI
          </Text>

          <Text
            style={[
              styles.subtitle,
              {
                color: colors.muted,
                fontSize: getFontSize(15, largeText),
              },
            ]}
          >
            Your campus-aware assistant for room insights, La Trobe questions, and document-based conversations.
          </Text>
        </View>

        <View
          style={[
            styles.infoCard,
            {
              backgroundColor: colors.card,
              borderColor: colors.border,
            },
          ]}
        >
          <Text
            style={[
              styles.infoTitle,
              {
                color: colors.text,
                fontSize: getFontSize(18, largeText),
              },
            ]}
          >
            Project-aligned chatbot experience
          </Text>
          <Text
            style={[
              styles.infoText,
              {
                color: colors.muted,
                fontSize: getFontSize(14, largeText),
              },
            ]}
          >
            Ask natural questions about campus data, room conditions, official information, and uploaded PDFs from one main assistant flow. :contentReference[oaicite:2]{index=2}
          </Text>
        </View>

        <Pressable
          style={[styles.button, { backgroundColor: colors.primary }]}
          onPress={() => router.push("/chat")}
        >
          <Text
            style={[
              styles.buttonText,
              {
                color: colors.white,
                fontSize: getFontSize(16, largeText),
              },
            ]}
          >
            Get Started
          </Text>
        </Pressable>
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
    paddingHorizontal: 24,
    paddingTop: 40,
    paddingBottom: 30,
    justifyContent: "space-between",
  },
  heroSection: {
    alignItems: "center",
    marginTop: 40,
  },
  logoCircle: {
    width: 110,
    height: 110,
    borderRadius: 55,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 2,
    marginBottom: 22,
  },
  logoText: {
    fontSize: 34,
    fontWeight: "900",
    letterSpacing: 1,
  },
  brandTitle: {
    fontWeight: "900",
  },
  subtitle: {
    textAlign: "center",
    marginTop: 12,
    lineHeight: 22,
    maxWidth: 320,
  },
  infoCard: {
    borderRadius: 24,
    padding: 20,
    borderWidth: 1,
  },
  infoTitle: {
    fontWeight: "800",
    marginBottom: 10,
  },
  infoText: {
    lineHeight: 22,
  },
  button: {
    borderRadius: 18,
    paddingVertical: 18,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonText: {
    fontWeight: "800",
  },
});