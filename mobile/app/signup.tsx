import { router } from "expo-router";
import React, { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { palette, getFontSize } from "../src/constants/theme";
import { useAppSettings } from "../src/context/AppSettingsContext";
import { SignupExtraUserData, useAuth } from "../src/context/AuthContext";

type RoleOption = SignupExtraUserData["role"];

export default function SignupScreen() {
  const { themeMode, largeText } = useAppSettings();
  const { signup, continueAsGuest } = useAuth();
  const colors = palette[themeMode];

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<RoleOption>("student");
  const [campus, setCampus] = useState("");
  const [course, setCourse] = useState("");
  const [yearOfStudy, setYearOfStudy] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSignup = async () => {
    setErrorMessage(null);

    if (!email || !password || !confirmPassword) {
      setErrorMessage("Please fill in email and password fields.");
      return;
    }

    if (!fullName.trim()) {
      setErrorMessage("Full name is required.");
      return;
    }

    if (password !== confirmPassword) {
      setErrorMessage("Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      setErrorMessage("Password must be at least 6 characters.");
      return;
    }

    try {
      setLoading(true);
      await signup(email, password, {
        fullName: fullName.trim(),
        role,
        campus,
        course,
        yearOfStudy,
      });
      router.replace("/chat");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Something went wrong.";
      setErrorMessage(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.background }]}>
      <ScrollView
        contentContainerStyle={styles.container}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
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
            placeholder="Full Name"
            placeholderTextColor={colors.muted}
            autoCapitalize="words"
            value={fullName}
            onChangeText={setFullName}
            style={[
              styles.input,
              { backgroundColor: colors.card, color: colors.text, borderColor: colors.border },
            ]}
          />

          <View style={styles.roleContainer}>
            <Pressable
              onPress={() => setRole("student")}
              style={[
                styles.roleButton,
                {
                  backgroundColor: role === "student" ? colors.primary : colors.card,
                  borderColor: colors.border,
                },
              ]}
            >
              <Text
                style={{
                  color: role === "student" ? colors.white : colors.text,
                  fontWeight: "700",
                  fontSize: getFontSize(14, largeText),
                }}
              >
                Student
              </Text>
            </Pressable>
            <Pressable
              onPress={() => setRole("staff")}
              style={[
                styles.roleButton,
                {
                  backgroundColor: role === "staff" ? colors.primary : colors.card,
                  borderColor: colors.border,
                },
              ]}
            >
              <Text
                style={{
                  color: role === "staff" ? colors.white : colors.text,
                  fontWeight: "700",
                  fontSize: getFontSize(14, largeText),
                }}
              >
                Staff
              </Text>
            </Pressable>
          </View>

          <TextInput
            placeholder="Campus (optional)"
            placeholderTextColor={colors.muted}
            value={campus}
            onChangeText={setCampus}
            style={[
              styles.input,
              { backgroundColor: colors.card, color: colors.text, borderColor: colors.border },
            ]}
          />

          <TextInput
            placeholder="Course (optional)"
            placeholderTextColor={colors.muted}
            value={course}
            onChangeText={setCourse}
            style={[
              styles.input,
              { backgroundColor: colors.card, color: colors.text, borderColor: colors.border },
            ]}
          />

          <TextInput
            placeholder="Year of Study (optional)"
            placeholderTextColor={colors.muted}
            value={yearOfStudy}
            onChangeText={setYearOfStudy}
            keyboardType="number-pad"
            style={[
              styles.input,
              { backgroundColor: colors.card, color: colors.text, borderColor: colors.border },
            ]}
          />

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

          {errorMessage ? (
            <Text style={[styles.errorText, { fontSize: getFontSize(13, largeText) }]}>
              {errorMessage}
            </Text>
          ) : null}

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
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  container: {
    flexGrow: 1,
    paddingHorizontal: 24,
    justifyContent: "center",
    paddingVertical: 24,
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
  roleContainer: {
    flexDirection: "row",
    gap: 10,
  },
  roleButton: {
    flex: 1,
    borderWidth: 1,
    borderRadius: 14,
    paddingVertical: 12,
    alignItems: "center",
    justifyContent: "center",
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
  errorText: {
    color: "#DC2626",
    fontWeight: "600",
  },
  link: {
    textAlign: "center",
    fontWeight: "600",
    marginTop: 8,
  },
});