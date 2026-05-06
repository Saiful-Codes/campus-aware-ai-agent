import AsyncStorage from "@react-native-async-storage/async-storage";
import { router } from "expo-router";
import {
  ChevronRight,
  Clock,
  Info,
  MessageSquare,
  Moon,
  Plus,
  Settings,
  Trash2,
} from "lucide-react-native";
import React, { useCallback, useEffect, useState } from "react";
import {
  Alert,
  Linking,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { getFontSize, palette } from "../../src/constants/theme";
import { useAppSettings } from "../../src/context/AppSettingsContext";
import { useAuth } from "../../src/context/AuthContext";
import {
  createChatThread,
  deleteChatThread,
  subscribeChatThreads,
} from "../../src/lib/chatThreads";
import { doc, getDoc } from "firebase/firestore";
import { db } from "../../src/lib/firebase";

// ── Storage keys (must match chat.tsx) ───────────────────────────────────────
const THREADS_KEY = "campus_ai_threads_v2";
const ACTIVE_THREAD_KEY = "campus_ai_active_thread";

type ChatThread = {
  id: string;
  name: string;
  preview: string;
  updatedAt: number;
};

type UserProfileDoc = {
  fullName?: string;
  email?: string;
};

// ── Helpers ───────────────────────────────────────────────────────────────────
function getInitial(email: string | null | undefined, displayName: string | null | undefined, isGuest: boolean) {
  if (isGuest) return "G";
  if (displayName) return displayName.charAt(0).toUpperCase();
  if (email) return email.charAt(0).toUpperCase();
  return "U";
}

function getDisplayName(email: string | null | undefined, displayName: string | null | undefined, isGuest: boolean) {
  if (isGuest) return "Guest";
  if (displayName) return displayName;
  if (email) return email.split("@")[0];
  return "Campus User";
}

function formatDate(ts: number) {
  const d = new Date(ts);
  return d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}

// ── Reusable row ──────────────────────────────────────────────────────────────
type RowProps = {
  icon: React.ReactNode;
  label: string;
  sublabel?: string;
  onPress: () => void;
  colors: (typeof palette)["light"];
  largeText: boolean;
  danger?: boolean;
  right?: React.ReactNode;
};

function Row({ icon, label, sublabel, onPress, colors, largeText, danger, right }: RowProps) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [
        rowS.row,
        { backgroundColor: pressed ? colors.surface2 : "transparent" },
      ]}
    >
      <View style={[rowS.iconWrap, { backgroundColor: danger ? "#FEE2E2" : colors.surface }]}>
        {icon}
      </View>
      <View style={rowS.labelWrap}>
        <Text style={[rowS.label, { color: danger ? "#DC2626" : colors.text, fontSize: getFontSize(15, largeText) }]}>
          {label}
        </Text>
        {sublabel ? (
          <Text style={[rowS.sublabel, { color: colors.muted, fontSize: getFontSize(12, largeText) }]}>
            {sublabel}
          </Text>
        ) : null}
      </View>
      {right ?? <ChevronRight color={danger ? "#DC2626" : colors.muted} size={17} />}
    </Pressable>
  );
}

const rowS = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 13,
    borderRadius: 14,
  },
  iconWrap: {
    width: 36,
    height: 36,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
  },
  labelWrap: { flex: 1 },
  label: { fontWeight: "600" },
  sublabel: { marginTop: 1 },
});

// ── Thread history item ───────────────────────────────────────────────────────
function ThreadRow({
  thread,
  colors,
  largeText,
  onOpen,
  onDelete,
}: {
  thread: ChatThread;
  colors: (typeof palette)["light"];
  largeText: boolean;
  onOpen: () => void;
  onDelete: () => void;
}) {
  return (
    <View style={[threadS.row, { borderBottomColor: colors.border }]}>
      <View style={[threadS.dot, { backgroundColor: colors.primarySoft }]}>
        <MessageSquare color={colors.primary} size={13} />
      </View>
      <Pressable onPress={onOpen} style={threadS.info}>
        <Text
          style={[threadS.name, { color: colors.text, fontSize: getFontSize(14, largeText) }]}
          numberOfLines={1}
        >
          {thread.name}
        </Text>
        <Text style={[threadS.meta, { color: colors.muted, fontSize: getFontSize(11, largeText) }]}>
          {formatDate(thread.updatedAt)}
          {thread.preview ? ` · ${thread.preview.slice(0, 40)}` : ""}
        </Text>
      </Pressable>
      <Pressable onPress={onDelete} hitSlop={10} style={threadS.deleteBtn}>
        <Trash2 color={colors.muted} size={15} />
      </Pressable>
    </View>
  );
}

const threadS = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 11,
    gap: 12,
    borderBottomWidth: 1,
  },
  dot: {
    width: 30,
    height: 30,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  info: { flex: 1, minWidth: 0 },
  name: { fontWeight: "600", marginBottom: 2 },
  meta: { lineHeight: 15 },
  deleteBtn: { padding: 4, flexShrink: 0 },
});

// ── Main screen ───────────────────────────────────────────────────────────────
export default function ProfileScreen() {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];
  const { user, isGuest } = useAuth();
  const isAuthenticatedUser = !!user?.uid && !isGuest;

  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [showAllThreads, setShowAllThreads] = useState(false);
  const [isCreatingChat, setIsCreatingChat] = useState(false);
  const [profileFullName, setProfileFullName] = useState<string>("");
  const [profileEmail, setProfileEmail] = useState<string>("");

  const resolvedName = profileFullName || user?.displayName || user?.email?.split("@")[0] || "";
  const initial = getInitial(profileEmail || user?.email, resolvedName, isGuest);
  const displayName = getDisplayName(profileEmail || user?.email, resolvedName, isGuest);
  const email = isGuest ? "Browsing as guest" : profileEmail || user?.email || "";

  useEffect(() => {
    if (!user?.uid || isGuest) {
      setProfileFullName("");
      setProfileEmail("");
      return;
    }

    const loadProfile = async () => {
      try {
        const userRef = doc(db, "users", user.uid);
        const snapshot = await getDoc(userRef);

        if (!snapshot.exists()) {
          setProfileFullName(user.displayName ?? "");
          setProfileEmail(user.email ?? "");
          return;
        }

        const data = snapshot.data() as UserProfileDoc;
        setProfileFullName(data.fullName ?? user.displayName ?? "");
        setProfileEmail(data.email ?? user.email ?? "");
      } catch (error) {
        console.log("Failed to load user profile", error);
        setProfileFullName(user.displayName ?? "");
        setProfileEmail(user.email ?? "");
      }
    };

    loadProfile();
  }, [user?.uid, isGuest]);

  // ── Load threads ────────────────────────────────────────────────────────────
  useEffect(() => {
    if (isAuthenticatedUser && user?.uid) {
      const unsubscribe = subscribeChatThreads(
        user.uid,
        (remoteThreads) => {
          const mapped: ChatThread[] = remoteThreads.map((t) => ({
            id: t.id,
            name: t.title,
            preview: t.lastMessage,
            updatedAt: t.updatedAtMs,
          }));
          setThreads(mapped);
        },
        (error) => {
          console.log("Failed to load remote threads", error);
        }
      );

      return unsubscribe;
    }

    const load = async () => {
      try {
        const raw = await AsyncStorage.getItem(THREADS_KEY);
        if (raw) {
          const parsed: ChatThread[] = JSON.parse(raw);
          setThreads(parsed.sort((a, b) => b.updatedAt - a.updatedAt));
        }
      } catch { }
    };
    load();
  }, [isAuthenticatedUser, user?.uid]);

  const handleCreateNewChat = useCallback(async () => {
    if (isCreatingChat) return;

    if (isGuest || !user?.uid) {
      Alert.alert("Login required", "Sign in to create synced chat history.");
      return;
    }

    setIsCreatingChat(true);
    try {
      const chatId = await createChatThread(user.uid);
      router.push({ pathname: "/chat", params: { chatId } });
    } catch (error) {
      console.log("Create chat failed", error);
      Alert.alert("Could not create chat", "Please try again.");
    } finally {
      setIsCreatingChat(false);
    }
  }, [isCreatingChat, isGuest, user?.uid]);

  // ── Delete one thread ───────────────────────────────────────────────────────
  const deleteThread = useCallback(async (id: string) => {
    if (isAuthenticatedUser && user?.uid) {
      try {
        await deleteChatThread(user.uid, id);
      } catch (error) {
        console.log("Delete thread failed", error);
        Alert.alert("Could not delete chat", "Please try again.");
      }
      return;
    }

    const updated = threads.filter((t) => t.id !== id);
    setThreads(updated);
    try {
      await AsyncStorage.setItem(THREADS_KEY, JSON.stringify(updated));
      // Remove messages for this thread
      const rawMsgs = await AsyncStorage.getItem(`${THREADS_KEY}_messages`);
      if (rawMsgs) {
        const msgs = JSON.parse(rawMsgs);
        delete msgs[id];
        await AsyncStorage.setItem(`${THREADS_KEY}_messages`, JSON.stringify(msgs));
      }
      // If deleted thread was active, clear active pointer
      const activeId = await AsyncStorage.getItem(ACTIVE_THREAD_KEY);
      if (activeId === id) await AsyncStorage.removeItem(ACTIVE_THREAD_KEY);
    } catch { }
  }, [isAuthenticatedUser, user?.uid, threads]);

  const openThread = useCallback((chatId: string) => {
    router.push({ pathname: "/chat", params: { chatId } });
  }, []);

  const visibleThreads = showAllThreads ? threads : threads.slice(0, 4);

  return (
    <SafeAreaView style={[s.safe, { backgroundColor: colors.background }]}>
      <ScrollView
        contentContainerStyle={s.scroll}
        showsVerticalScrollIndicator={false}
      >
        {/* ── Page title ── */}
        <Text style={[s.pageTitle, { color: colors.text, fontSize: getFontSize(28, largeText) }]}>
          Profile
        </Text>

        {/* ── User card ── */}
        <View style={[s.userCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <View style={[s.avatarCircle, { backgroundColor: colors.primary }]}>
            <Text style={[s.avatarInitial, { fontSize: getFontSize(28, largeText) }]}>
              {initial}
            </Text>
          </View>
          <View style={s.userInfo}>
            <Text style={[s.userName, { color: colors.text, fontSize: getFontSize(18, largeText) }]}>
              {displayName}
            </Text>
            <Text style={[s.userEmail, { color: colors.muted, fontSize: getFontSize(13, largeText) }]}>
              {email}
            </Text>
          </View>
          <View style={[s.badge, { backgroundColor: colors.primarySoft }]}>
            <Text style={[s.badgeText, { color: colors.primary, fontSize: getFontSize(11, largeText) }]}>
              La Trobe
            </Text>
          </View>
        </View>

        {/* ── Chat history ── */}
        <Text style={[s.sectionLabel, { color: colors.muted, fontSize: getFontSize(11, largeText) }]}>
          CHAT HISTORY
        </Text>
        <Pressable
          onPress={handleCreateNewChat}
          disabled={isCreatingChat}
          style={[s.newChatBtn, { backgroundColor: colors.primary, opacity: isCreatingChat ? 0.6 : 1 }]}
        >
          <Plus color="#fff" size={16} />
          <Text style={[s.newChatText, { fontSize: getFontSize(14, largeText) }]}>
            {isCreatingChat ? "Creating..." : "New Chat"}
          </Text>
        </Pressable>
        <View style={[s.section, { backgroundColor: colors.card, borderColor: colors.border }]}>
          {threads.length === 0 ? (
            <View style={s.emptyHistory}>
              <Clock color={colors.muted} size={20} />
              <Text style={[s.emptyText, { color: colors.muted, fontSize: getFontSize(13, largeText) }]}>
                No conversations yet
              </Text>
            </View>
          ) : (
            <>
              {visibleThreads.map((thread, i) => (
                <View key={thread.id}>
                  <ThreadRow
                    thread={thread}
                    colors={colors}
                    largeText={largeText}
                    onOpen={() => openThread(thread.id)}
                    onDelete={() => deleteThread(thread.id)}
                  />
                </View>
              ))}

              {threads.length > 4 && (
                <Pressable
                  onPress={() => setShowAllThreads((p) => !p)}
                  style={[s.showMore, { borderTopColor: colors.border }]}
                >
                  <Text style={[s.showMoreText, { color: colors.primary, fontSize: getFontSize(13, largeText) }]}>
                    {showAllThreads ? "Show less" : `Show ${threads.length - 4} more`}
                  </Text>
                </Pressable>
              )}

            </>
          )}
        </View>

        {/* ── Settings ── */}
        <Text style={[s.sectionLabel, { color: colors.muted, fontSize: getFontSize(11, largeText) }]}>
          SETTINGS
        </Text>
        <View style={[s.section, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <Row
            icon={<Settings color={colors.primary} size={17} strokeWidth={2} />}
            label="App Settings"
            sublabel="Theme, text size, accessibility"
            onPress={() => router.push("/settings")}
            colors={colors}
            largeText={largeText}
          />
          <View style={[s.divider, { backgroundColor: colors.border }]} />
          <Row
            icon={<Moon color={colors.primary} size={17} strokeWidth={2} />}
            label="Appearance"
            sublabel={themeMode === "dark" ? "Dark mode" : "Light mode"}
            onPress={() => router.push("/settings")}
            colors={colors}
            largeText={largeText}
          />
          <View style={[s.divider, { backgroundColor: colors.border }]} />
          {/* Suggested: Send Feedback */}
          <Row
            icon={<Info color={colors.primary} size={17} strokeWidth={2} />}
            label="Send Feedback"
            sublabel="Help us improve Campus AI"
            onPress={() =>
              Linking.openURL("mailto:feedback@campus-ai.com?subject=Campus AI Feedback")
            }
            colors={colors}
            largeText={largeText}
          />
        </View>

        {/* ── Footer ── */}
        <Text style={[s.footer, { color: colors.muted, fontSize: getFontSize(11, largeText) }]}>
          Campus-Aware AI · Cisco – La Trobe Centre for AI & IoT{"\n"}v1.0.0
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1 },
  scroll: {
    paddingHorizontal: 20,
    paddingTop: 18,
    paddingBottom: 48,
  },
  pageTitle: {
    fontWeight: "900",
    marginBottom: 20,
  },

  // User card
  userCard: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
    borderRadius: 20,
    borderWidth: 1,
    padding: 16,
    marginBottom: 24,
  },
  avatarCircle: {
    width: 54,
    height: 54,
    borderRadius: 16,
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  avatarInitial: {
    color: "#fff",
    fontWeight: "900",
  },
  userInfo: { flex: 1, minWidth: 0 },
  userName: { fontWeight: "800", marginBottom: 2 },
  userEmail: { lineHeight: 17 },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 20,
    flexShrink: 0,
  },
  badgeText: { fontWeight: "700" },

  // Section
  sectionLabel: {
    fontWeight: "700",
    letterSpacing: 0.8,
    marginBottom: 8,
    paddingHorizontal: 4,
    textTransform: "uppercase",
  },
  section: {
    borderRadius: 20,
    borderWidth: 1,
    marginBottom: 24,
    overflow: "hidden",
  },
  newChatBtn: {
    marginBottom: 10,
    borderRadius: 14,
    paddingVertical: 12,
    paddingHorizontal: 14,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  },
  newChatText: {
    color: "#fff",
    fontWeight: "700",
  },
  divider: { height: 1, marginHorizontal: 16 },

  // Chat history
  emptyHistory: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingHorizontal: 16,
    paddingVertical: 18,
  },
  emptyText: {},
  showMore: {
    paddingVertical: 12,
    alignItems: "center",
    borderTopWidth: 1,
  },
  showMoreText: { fontWeight: "600" },

  // Footer
  footer: {
    textAlign: "center",
    lineHeight: 18,
  },
});
