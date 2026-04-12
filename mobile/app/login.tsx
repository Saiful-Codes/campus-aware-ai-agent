import { router } from "expo-router";
import React, { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { palette, getFontSize } from "../src/constants/theme";
import { useAppSettings } from "../src/context/AppSettingsContext";
import { useAuth } from "../src/context/AuthContext";

export default function LoginScreen() {
  const { themeMode, largeText } = useAppSettings();
  const { login } = useAuth();
  const colors = palette[themeMode];

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert("Missing fields", "Please enter email and password.");
      return;
    }

    try {
      setLoading(true);
      await login(email, password);
      router.replace("/chat");
    } catch (error: any) {
      Alert.alert("Login failed", error.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.background }]}>
      <View style={styles.container}>
        <Text
          style={[
            styles.title,
            { color: colors.primary, fontSize: getFontSize(30, largeText) },
          ]}
        >
          Welcome Back
        </Text>

        <Text
          style={[
            styles.subtitle,
            { color: colors.muted, fontSize: getFontSize(15, largeText) },
          ]}
        >
          Login to continue using Campus AI
        </Text>

        <View style={styles.form}>
          <TextInput
            placeholder="Email"
            placeholderTextColor={colors.muted}
            keyboardType="email-address"
            autoCapitalize="none"
            value={email}
            onChangeText={setEmail}
            style={[
              styles.input,
              { backgroundColor: colors.card, color: colors.text, borderColor: colors.border },
            ]}
          />

          <TextInput
            placeholder="Password"
            placeholderTextColor={colors.muted}
            secureTextEntry
            value={password}
            onChangeText={setPassword}
            style={[
              styles.input,
              { backgroundColor: colors.card, color: colors.text, borderColor: colors.border },
            ]}
          />

          <Pressable
            style={[styles.button, { backgroundColor: colors.primary }]}
            onPress={handleLogin}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color={colors.white} />
            ) : (
              <Text
                style={[
                  styles.buttonText,
                  { color: colors.white, fontSize: getFontSize(16, largeText) },
                ]}
              >
                Login
              </Text>
            )}
          </Pressable>

          <Pressable onPress={() => router.push("/signup")}>
            <Text
              style={[
                styles.link,
                { color: colors.primary, fontSize: getFontSize(14, largeText) },
              ]}
            >
              Don’t have an account? Sign Up
            </Text>
          </Pressable>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  container: {
    flex: 1,
    paddingHorizontal: 24,
    justifyContent: "center",
  },
  title: {
    fontWeight: "900",
    textAlign: "center",
  },
  subtitle: {
    textAlign: "center",
    marginTop: 10,
    marginBottom: 30,
  },
  form: {
    gap: 16,
  },
  input: {
    borderWidth: 1,
    borderRadius: 14,
    paddingHorizontal: 16,
    paddingVertical: 14,
  },
  button: {
    borderRadius: 16,
    paddingVertical: 16,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 8,
  },
  buttonText: {
    fontWeight: "800",
  },
  link: {
    textAlign: "center",
    fontWeight: "600",
    marginTop: 8,
  },
});