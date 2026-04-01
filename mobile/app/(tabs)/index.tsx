import { router } from "expo-router";
import React from "react";
import { Image, Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";
import { getFontSize, palette } from "../../src/constants/theme";
import { useAppSettings } from "../../src/context/AppSettingsContext";

export default function HomeScreen() {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.background }]}>
      <View style={styles.container}>
        
        <View style={styles.heroSection}>
          {/* Logo */}
          <Image
            source={require("../../assets/images/latrobe-logo.png")}
            style={styles.logo}
          />

          {/* Title */}
          <Text
            style={[
              styles.brandTitle,
              {
                color: colors.primary,
                fontSize: getFontSize(34, largeText),
              },
            ]}
          >
            Campus AI
          </Text>

          {/* ✅ Small description (added back) */}
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

        {/* Button */}
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
    marginTop: 80,
  },
  logo: {
    width: 160,
    height: 90,
    resizeMode: "contain",
    marginBottom: 24,
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