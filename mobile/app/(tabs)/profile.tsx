import { router } from "expo-router";
import {
  BookOpen,
  Building2,
  ChevronRight,
  LogOut,
  MessageSquare,
  Moon,
  Settings,
  User,
} from "lucide-react-native";
import React from "react";
import {
  Alert,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { getFontSize, palette } from "../../src/constants/theme";
import { useAppSettings } from "../../src/context/AppSettingsContext";

// ── Stat card ────────────────────────────────────────────────────────────────
function StatCard({
  label,
  value,
  colors,
  largeText,
}: {
  label: string;
  value: string;
  colors: (typeof palette)["light"];
  largeText: boolean;
}) {
  return (
    <View
      style={[
        statStyles.card,
        { backgroundColor: colors.card, borderColor: colors.border },
      ]}
    >
      <Text
        style={[
          statStyles.value,
          { color: colors.primary, fontSize: getFontSize(22, largeText) },
        ]}
      >
        {value}
      </Text>
      <Text
        style={[
          statStyles.label,
          { color: colors.muted, fontSize: getFontSize(11, largeText) },
        ]}
      >
        {label}
      </Text>
    </View>
  );
}

const statStyles = StyleSheet.create({
  card: {
    flex: 1,
    borderRadius: 18,
    borderWidth: 1,
    paddingVertical: 16,
    paddingHorizontal: 12,
    alignItems: "center",
    gap: 4,
  },
  value: { fontWeight: "900" },
  label: { fontWeight: "600", textTransform: "uppercase", letterSpacing: 0.5, textAlign: "center" },
});

// ── Menu row ─────────────────────────────────────────────────────────────────
function MenuRow({
  icon,
  label,
  onPress,
  colors,
  largeText,
  danger,
}: {
  icon: React.ReactNode;
  label: string;
  onPress: () => void;
  colors: (typeof palette)["light"];
  largeText: boolean;
  danger?: boolean;
}) {
  return (
    <Pressable
      style={({ pressed }) => [
        rowStyles.row,
        { backgroundColor: pressed ? colors.surface2 : "transparent" },
      ]}
      onPress={onPress}
    >
      <View style={[rowStyles.iconWrap, { backgroundColor: danger ? "#FEE2E2" : colors.surface }]}>
        {icon}
      </View>
      <Text
        style={[
          rowStyles.label,
          {
            color: danger ? "#DC2626" : colors.text,
            fontSize: getFontSize(15, largeText),
          },
        ]}
      >
        {label}
      </Text>
      <ChevronRight color={danger ? "#DC2626" : colors.muted} size={18} />
    </Pressable>
  );
}

const rowStyles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 13,
    gap: 14,
    borderRadius: 14,
  },
  iconWrap: {
    width: 38,
    height: 38,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
  },
  label: { flex: 1, fontWeight: "600" },
});

// ── Main screen ───────────────────────────────────────────────────────────────
export default function ProfileScreen() {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];

  const handleLogout = () => {
    Alert.alert("Sign out", "Are you sure you want to sign out?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Sign out",
        style: "destructive",
        onPress: () => {
          // TODO: clear auth state and navigate to login
          router.replace("/login");
        },
      },
    ]);
  };

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.background }]}>
      <ScrollView
        contentContainerStyle={styles.scroll}
        showsVerticalScrollIndicator={false}
      >
        {/* ── Page title ── */}
        <Text
          style={[
            styles.pageTitle,
            { color: colors.text, fontSize: getFontSize(28, largeText) },
          ]}
        >
          Profile
        </Text>

        {/* ── Avatar + name card ── */}
        <View
          style={[
            styles.heroCard,
            { backgroundColor: colors.card, borderColor: colors.border },
          ]}
        >
          {/* Avatar circle */}
          <View style={[styles.avatarRing, { borderColor: colors.primary }]}>
            <View style={[styles.avatar, { backgroundColor: colors.primary }]}>
              <User color="#fff" size={32} strokeWidth={2.5} />
            </View>
          </View>

          <Text
            style={[
              styles.userName,
              { color: colors.text, fontSize: getFontSize(20, largeText) },
            ]}
          >
            Campus User
          </Text>

          <View style={[styles.roleBadge, { backgroundColor: colors.primarySoft }]}>
            <Text style={[styles.roleText, { color: colors.primary, fontSize: getFontSize(12, largeText) }]}>
              La Trobe University
            </Text>
          </View>
        </View>

        {/* ── Stats row ── */}
        <View style={styles.statsRow}>
          <StatCard label="Chats" value="—" colors={colors} largeText={largeText} />
          <StatCard label="Rooms queried" value="—" colors={colors} largeText={largeText} />
          <StatCard label="Docs uploaded" value="—" colors={colors} largeText={largeText} />
        </View>

        {/* ── Campus section ── */}
        <Text style={[styles.sectionLabel, { color: colors.muted, fontSize: getFontSize(12, largeText) }]}>
          CAMPUS
        </Text>
        <View style={[styles.section, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <MenuRow
            icon={<Building2 color={colors.primary} size={18} strokeWidth={2} />}
            label="Bundoora Campus"
            onPress={() => {}}
            colors={colors}
            largeText={largeText}
          />
          <View style={[styles.divider, { backgroundColor: colors.border }]} />
          <MenuRow
            icon={<BookOpen color={colors.primary} size={18} strokeWidth={2} />}
            label="PDF Documents"
            onPress={() => {}}
            colors={colors}
            largeText={largeText}
          />
          <View style={[styles.divider, { backgroundColor: colors.border }]} />
          <MenuRow
            icon={<MessageSquare color={colors.primary} size={18} strokeWidth={2} />}
            label="Chat History"
            onPress={() => {}}
            colors={colors}
            largeText={largeText}
          />
        </View>

        {/* ── Preferences section ── */}
        <Text style={[styles.sectionLabel, { color: colors.muted, fontSize: getFontSize(12, largeText) }]}>
          PREFERENCES
        </Text>
        <View style={[styles.section, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <MenuRow
            icon={<Settings color={colors.primary} size={18} strokeWidth={2} />}
            label="Settings"
            onPress={() => router.push("/settings")}
            colors={colors}
            largeText={largeText}
          />
          <View style={[styles.divider, { backgroundColor: colors.border }]} />
          <MenuRow
            icon={<Moon color={colors.primary} size={18} strokeWidth={2} />}
            label={`Appearance: ${themeMode === "dark" ? "Dark" : "Light"}`}
            onPress={() => router.push("/settings")}
            colors={colors}
            largeText={largeText}
          />
        </View>

        {/* ── Account section ── */}
        <Text style={[styles.sectionLabel, { color: colors.muted, fontSize: getFontSize(12, largeText) }]}>
          ACCOUNT
        </Text>
        <View style={[styles.section, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <MenuRow
            icon={<LogOut color="#DC2626" size={18} strokeWidth={2} />}
            label="Sign out"
            onPress={handleLogout}
            colors={colors}
            largeText={largeText}
            danger
          />
        </View>

        {/* ── Footer ── */}
        <Text style={[styles.footer, { color: colors.muted, fontSize: getFontSize(12, largeText) }]}>
          Campus-Aware AI Agent · Cisco – La Trobe Centre for AI & IoT
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  scroll: {
    paddingHorizontal: 20,
    paddingTop: 18,
    paddingBottom: 40,
  },
  pageTitle: {
    fontWeight: "900",
    marginBottom: 20,
  },
  heroCard: {
    borderRadius: 24,
    borderWidth: 1,
    padding: 24,
    alignItems: "center",
    marginBottom: 16,
    gap: 10,
  },
  avatarRing: {
    width: 80,
    height: 80,
    borderRadius: 28,
    borderWidth: 3,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 4,
  },
  avatar: {
    width: 68,
    height: 68,
    borderRadius: 22,
    alignItems: "center",
    justifyContent: "center",
  },
  userName: {
    fontWeight: "800",
  },
  roleBadge: {
    paddingHorizontal: 14,
    paddingVertical: 5,
    borderRadius: 20,
  },
  roleText: {
    fontWeight: "700",
    letterSpacing: 0.3,
  },
  statsRow: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 24,
  },
  sectionLabel: {
    fontWeight: "700",
    letterSpacing: 0.8,
    marginBottom: 8,
    paddingHorizontal: 4,
  },
  section: {
    borderRadius: 20,
    borderWidth: 1,
    marginBottom: 24,
    overflow: "hidden",
  },
  divider: {
    height: 1,
    marginHorizontal: 16,
  },
  footer: {
    textAlign: "center",
    lineHeight: 20,
    marginTop: 4,
  },
});
