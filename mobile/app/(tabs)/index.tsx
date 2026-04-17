import { router } from "expo-router";
import React from "react";
import {
  Image,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { getFontSize, palette } from "../../src/constants/theme";
import { useAppSettings } from "../../src/context/AppSettingsContext";
import { useAuth } from "../../src/context/AuthContext";

export default function HomeScreen() {
  const { themeMode, largeText } = useAppSettings();
  const { continueAsGuest } = useAuth();
  const colors = palette[themeMode];

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.background }]}>
      <View style={styles.container}>
        <View style={styles.heroSection}>
          <Image
            source={require("../../assets/images/latrobe-logo.png")}
            style={styles.logo}
          />

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

          <Text
            style={[
              styles.subtitle,
              {
                color: colors.muted,
                fontSize: getFontSize(15, largeText),
              },
            ]}
          >
            Your campus-aware assistant for room insights, La Trobe questions,
            and document-based conversations.
          </Text>
        </View>

        <View style={styles.buttonGroup}>
          <Pressable
            style={[styles.button, { backgroundColor: colors.primary }]}
            onPress={() => router.push("/login")}
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
              Login
            </Text>
          </Pressable>

          <Pressable
            style={[
              styles.outlineButton,
              { borderColor: colors.primary, backgroundColor: colors.card },
            ]}
            onPress={() => router.push("/signup")}
          >
            <Text
              style={[
                styles.outlineButtonText,
                {
                  color: colors.primary,
                  fontSize: getFontSize(16, largeText),
                },
              ]}
            >
              Sign Up
            </Text>
          </Pressable>

          <Pressable
            onPress={() => {
              continueAsGuest();
              router.replace("/chat");
            }}
          >
            <Text
              style={[
                styles.guestText,
                {
                  color: colors.muted,
                  fontSize: getFontSize(14, largeText),
                },
              ]}
            >
              Continue as Guest
            </Text>
          </Pressable>
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
  buttonGroup: {
    gap: 14,
    marginBottom: 20,
  },
  button: {
    borderRadius: 18,
    paddingVertical: 18,
    alignItems: "center",
    justifyContent: "center",
  },
  outlineButton: {
    borderRadius: 18,
    paddingVertical: 18,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1.5,
  },
  buttonText: {
    fontWeight: "800",
  },
  outlineButtonText: {
    fontWeight: "800",
  },
  guestText: {
    textAlign: "center",
    marginTop: 6,
    fontWeight: "600",
  },
});