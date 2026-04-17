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

export default function SignupScreen() {
  const { themeMode, largeText } = useAppSettings();
  const { signup, continueAsGuest } = useAuth();
  const colors = palette[themeMode];

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignup = async () => {
    if (!email || !password || !confirmPassword) {
      Alert.alert("Missing fields", "Please fill all fields.");
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert("Password mismatch", "Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      Alert.alert("Weak password", "Password must be at least 6 characters.");
      return;
    }

    try {
      setLoading(true);
      await signup(email, password);
      router.replace("/chat");
    } catch (error: any) {
      Alert.alert("Signup failed", error.message || "Something went wrong.");
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
          Create Account
        </Text>

        <Text
          style={[
            styles.subtitle,
            { color: colors.muted, fontSize: getFontSize(15, largeText) },
          ]}
        >
          Sign up to start using Campus AI
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

          <TextInput
            placeholder="Confirm Password"
            placeholderTextColor={colors.muted}
            secureTextEntry
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            style={[
              styles.input,
              { backgroundColor: colors.card, color: colors.text, borderColor: colors.border },
            ]}
          />

          <Pressable
            style={[styles.button, { backgroundColor: colors.primary }]}
            onPress={handleSignup}
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
                Sign Up
              </Text>
            )}
          </Pressable>

          <Pressable onPress={() => router.push("/login")}>
            <Text
              style={[
                styles.link,
                { color: colors.primary, fontSize: getFontSize(14, largeText) },
              ]}
            >
              Already have an account? Login
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
                styles.link,
                { color: colors.muted, fontSize: getFontSize(14, largeText) },
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