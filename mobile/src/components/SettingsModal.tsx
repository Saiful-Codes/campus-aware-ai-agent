import { X } from "lucide-react-native";
import React from "react";
import {
  Alert,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { getFontSize, palette } from "../constants/theme";
import { useAppSettings } from "../context/AppSettingsContext";
import { useAuth } from "../context/AuthContext";
import { router } from "expo-router";

type Props = {
  visible: boolean;
  onClose: () => void;
};

export default function SettingsModal({ visible, onClose }: Props) {
  const { themeMode, largeText, setThemeMode, setLargeText } = useAppSettings();
  const { user, logout } = useAuth();
  const colors = palette[themeMode];

  const performLogout = async () => {
    try {
      await logout();
      onClose();
      router.replace("/login");
    } catch (error: any) {
      Alert.alert("Error", error?.message || "Logout failed");
    }
  };

  const handleLogout = () => {
    if (Platform.OS === "web") {
      // @ts-ignore
      const confirmed = window.confirm("Are you sure you want to log out?");
      if (confirmed) performLogout();
      return;
    }
    Alert.alert("Log out", "Are you sure you want to log out?", [
      { text: "Cancel", style: "cancel" },
      { text: "Log out", style: "destructive", onPress: performLogout },
    ]);
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent
      onRequestClose={onClose}
    >
      <View style={styles.overlay}>
        <Pressable style={styles.backdrop} onPress={onClose} />
        <SafeAreaView
          edges={["bottom"]}
          style={[styles.sheet, { backgroundColor: colors.background }]}
        >
          {/* Handle + header */}
          <View style={[styles.header, { borderBottomColor: colors.border }]}>
            <View style={[styles.handle, { backgroundColor: colors.border }]} />
            <Text style={[styles.title, { color: colors.text, fontSize: getFontSize(20, largeText) }]}>
              Settings
            </Text>
            <Pressable onPress={onClose} style={styles.closeBtn} hitSlop={10}>
              <X color={colors.text} size={22} />
            </Pressable>
          </View>

          <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scroll}>
            {/* Account info */}
            {user && (
              <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}>
                <Text style={[styles.cardTitle, { color: colors.text, fontSize: getFontSize(15, largeText) }]}>
                  Logged in as
                </Text>
                <Text style={[styles.cardValue, { color: colors.muted, fontSize: getFontSize(13, largeText) }]}>
                  {user.email}
                </Text>
              </View>
            )}

            {/* Dark mode */}
            <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <View style={styles.cardRow}>
                <View style={styles.cardText}>
                  <Text style={[styles.cardTitle, { color: colors.text, fontSize: getFontSize(15, largeText) }]}>
                    Dark Mode
                  </Text>
                  <Text style={[styles.cardSub, { color: colors.muted, fontSize: getFontSize(13, largeText) }]}>
                    Switch between light and dark appearance
                  </Text>
                </View>
                <Switch
                  value={themeMode === "dark"}
                  onValueChange={(v) => setThemeMode(v ? "dark" : "light")}
                  trackColor={{ false: colors.border, true: colors.primary }}
                  thumbColor={colors.white}
                  ios_backgroundColor={colors.border}
                />
              </View>
            </View>

            {/* Large text */}
            <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <View style={styles.cardRow}>
                <View style={styles.cardText}>
                  <Text style={[styles.cardTitle, { color: colors.text, fontSize: getFontSize(15, largeText) }]}>
                    Large Text
                  </Text>
                  <Text style={[styles.cardSub, { color: colors.muted, fontSize: getFontSize(13, largeText) }]}>
                    Increase font size for readability
                  </Text>
                </View>
                <Switch
                  value={largeText}
                  onValueChange={setLargeText}
                  trackColor={{ false: colors.border, true: colors.primary }}
                  thumbColor={colors.white}
                  ios_backgroundColor={colors.border}
                />
              </View>
            </View>

            {/* About */}
            <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <Text style={[styles.cardTitle, { color: colors.text, fontSize: getFontSize(15, largeText) }]}>
                About Campus AI
              </Text>
              <Text style={[styles.cardSub, { color: colors.muted, fontSize: getFontSize(13, largeText), marginTop: 6 }]}>
                A chatbot-first campus assistant supporting telemetry, database, PDF, and campus information workflows.{"\n"}v1.0.0
              </Text>
            </View>

            {/* Logout */}
            {user && (
              <Pressable
                style={({ pressed }) => [
                  styles.logoutBtn,
                  { backgroundColor: colors.primary, opacity: pressed ? 0.8 : 1 },
                ]}
                onPress={handleLogout}
              >
                <Text style={[styles.logoutText, { fontSize: getFontSize(16, largeText) }]}>
                  Log out
                </Text>
              </Pressable>
            )}
          </ScrollView>
        </SafeAreaView>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    justifyContent: "flex-end",
  },
  backdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,0,0,0.5)",
  },
  sheet: {
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: "80%",
    shadowColor: "#000",
    shadowOpacity: 0.2,
    shadowRadius: 20,
    shadowOffset: { width: 0, height: -4 },
    elevation: 12,
  },
  header: {
    alignItems: "center",
    paddingTop: 12,
    paddingBottom: 14,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    position: "relative",
  },
  handle: {
    width: 36,
    height: 4,
    borderRadius: 2,
    marginBottom: 10,
  },
  title: { fontWeight: "900" },
  closeBtn: {
    position: "absolute",
    right: 18,
    top: 14,
    padding: 4,
  },
  scroll: {
    padding: 20,
    paddingBottom: 32,
  },
  card: {
    borderRadius: 18,
    borderWidth: 1,
    padding: 16,
    marginBottom: 12,
  },
  cardRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  cardText: { flex: 1 },
  cardTitle: { fontWeight: "700", marginBottom: 2 },
  cardValue: { lineHeight: 18 },
  cardSub: { lineHeight: 18 },
  logoutBtn: {
    marginTop: 8,
    borderRadius: 16,
    paddingVertical: 15,
    alignItems: "center",
  },
  logoutText: { color: "#fff", fontWeight: "800" },
});
