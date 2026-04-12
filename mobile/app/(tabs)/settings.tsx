import React from "react";
import {
  SafeAreaView,
  StyleSheet,
  Switch,
  Text,
  View,
  Pressable,
  Alert,
} from "react-native";
import { router } from "expo-router";
import { getFontSize, palette } from "../../src/constants/theme";
import { useAppSettings } from "../../src/context/AppSettingsContext";
import { useAuth } from "../../src/context/AuthContext"; // ✅ add this

export default function SettingsScreen() {
  const { themeMode, largeText, setThemeMode, setLargeText } = useAppSettings();
  const { logout, user } = useAuth(); // ✅ get logout + user
  const colors = palette[themeMode];

  const handleLogout = async () => {
    Alert.alert("Logout", "Are you sure you want to logout?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Logout",
        style: "destructive",
        onPress: async () => {
          try {
            await logout();
            router.replace("/"); // go back to home
          } catch (error: any) {
            Alert.alert("Error", error.message || "Logout failed");
          }
        },
      },
    ]);
  };

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

        {/* 🔐 Account Info */}
        {user && (
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
                { color: colors.text, fontSize: getFontSize(17, largeText) },
              ]}
            >
              Logged in as
            </Text>
            <Text
              style={[
                styles.cardText,
                { color: colors.muted, fontSize: getFontSize(14, largeText) },
              ]}
            >
              {user.email}
            </Text>
          </View>
        )}

        {/* 🌙 Dark Mode */}
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

        {/* 🔠 Large Text */}
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

        {/* ℹ️ About */}
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
            This interface is designed for a chatbot-first campus assistant that can support telemetry, database, PDF, and official campus information workflows.
          </Text>
        </View>

        {/* 🚪 Logout */}
        {user && (
          <Pressable
            style={[
              styles.logoutButton,
              { backgroundColor: colors.primary },
            ]}
            onPress={handleLogout}
          >
            <Text
              style={[
                styles.logoutText,
                {
                  color: colors.white,
                  fontSize: getFontSize(16, largeText),
                },
              ]}
            >
              Logout
            </Text>
          </Pressable>
        )}
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
  logoutButton: {
    marginTop: 10,
    borderRadius: 18,
    paddingVertical: 16,
    alignItems: "center",
    justifyContent: "center",
  },
  logoutText: {
    fontWeight: "800",
  },
});