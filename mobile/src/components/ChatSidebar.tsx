import {
  Check,
  ChevronUp,
  LogOut,
  MessageSquare,
  Pencil,
  Plus,
  Settings,
  Trash2,
  User,
  X,
} from "lucide-react-native";
import React, { useState } from "react";
import {
  Animated,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableWithoutFeedback,
  View,
} from "react-native";
import { getFontSize, palette } from "../constants/theme";
import { useAppSettings } from "../context/AppSettingsContext";

export type ChatThread = {
  id: string;
  name: string;
  preview: string;
  updatedAt: number;
};

type Props = {
  visible: boolean;
  threads: ChatThread[];
  activeThreadId: string;
  onSelectThread: (id: string) => void;
  onNewThread: () => void;
  onDeleteThread: (id: string) => void;
  onRenameThread: (id: string, name: string) => void;
  onClose: () => void;
  translateX: Animated.Value;
  isCreatingThread?: boolean;
  isSwitchingThread?: boolean;
  // User section
  userInitial: string;
  userDisplayName: string;
  planLabel?: string;
  onOpenProfile: () => void;
  onOpenSettings: () => void;
  onLogout: () => void;
  // Wide-screen persistent mode (web)
  persistentMode?: boolean;
};

function formatRelativeTime(ts: number): string {
  const diff = Date.now() - ts;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days}d ago`;
  return new Date(ts).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function PanelContent({
  threads,
  activeThreadId,
  onSelectThread,
  onNewThread,
  onDeleteThread,
  onRenameThread,
  onClose,
  isCreatingThread,
  isSwitchingThread,
  userInitial,
  userDisplayName,
  planLabel,
  onOpenProfile,
  onOpenSettings,
  onLogout,
  persistentMode,
}: Omit<Props, "visible" | "translateX">) {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];
  const [editingThreadId, setEditingThreadId] = useState<string | null>(null);
  const [draftName, setDraftName] = useState("");
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);

  const startRename = (threadId: string, currentName: string) => {
    setEditingThreadId(threadId);
    setDraftName(currentName);
  };

  const cancelRename = () => {
    setEditingThreadId(null);
    setDraftName("");
  };

  const submitRename = (threadId: string) => {
    const nextName = draftName.trim();
    if (!nextName) return;
    onRenameThread(threadId, nextName);
    cancelRename();
  };

  return (
    <View style={styles.panelInner}>
      {/* Header */}
      <View style={[styles.sidebarHeader, { borderBottomColor: colors.border, paddingTop: persistentMode ? 20 : 56 }]}>
        <Text style={[styles.sidebarTitle, { color: colors.primary, fontSize: getFontSize(18, largeText) }]}>
          Campus AI
        </Text>
        <Pressable onPress={onClose} style={styles.closeBtn} hitSlop={10}>
          <X color={colors.text} size={20} />
        </Pressable>
      </View>

      {/* New Chat button */}
      <Pressable
        onPress={onNewThread}
        disabled={isCreatingThread}
        style={[styles.newChatBtn, { backgroundColor: colors.primary }]}
      >
        <Plus color="#fff" size={16} />
        <Text style={[styles.newChatText, { fontSize: getFontSize(14, largeText) }]}>
          {isCreatingThread ? "Creating..." : "New Chat"}
        </Text>
      </Pressable>

      {/* Thread list */}
      <ScrollView
        style={styles.threadList}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: 8 }}
      >
        {threads.length === 0 && (
          <Text style={[styles.emptyText, { color: colors.muted, fontSize: getFontSize(13, largeText) }]}>
            No conversations yet
          </Text>
        )}
        {threads.map((thread) => {
          const isActive = thread.id === activeThreadId;
          const isEditing = editingThreadId === thread.id;
          return (
            <Pressable
              key={thread.id}
              onPress={() => {
                if (!isEditing) onSelectThread(thread.id);
              }}
              disabled={isSwitchingThread}
              style={[
                styles.threadItem,
                isActive && { backgroundColor: colors.primarySoft },
                { borderColor: isActive ? colors.primary : "transparent" },
              ]}
            >
              <MessageSquare
                color={isActive ? colors.primary : colors.muted}
                size={15}
                style={styles.threadIcon}
              />
              <View style={styles.threadInfo}>
                {isEditing ? (
                  <TextInput
                    value={draftName}
                    onChangeText={setDraftName}
                    autoFocus
                    maxLength={60}
                    style={[
                      styles.renameInput,
                      { color: colors.text, borderColor: colors.border, fontSize: getFontSize(12, largeText) },
                    ]}
                    placeholder="Thread name"
                    placeholderTextColor={colors.muted}
                    onSubmitEditing={() => submitRename(thread.id)}
                  />
                ) : (
                  <>
                    <Text
                      style={[
                        styles.threadName,
                        { color: isActive ? colors.primary : colors.text, fontSize: getFontSize(13, largeText) },
                      ]}
                      numberOfLines={1}
                    >
                      {thread.name}
                    </Text>
                    <Text
                      style={[styles.threadPreview, { color: colors.muted, fontSize: getFontSize(11, largeText) }]}
                      numberOfLines={1}
                    >
                      {formatRelativeTime(thread.updatedAt)} · {thread.preview || "No messages yet"}
                    </Text>
                  </>
                )}
              </View>
              {isEditing ? (
                <>
                  <Pressable
                    onPress={() => submitRename(thread.id)}
                    disabled={!draftName.trim() || isSwitchingThread}
                    hitSlop={8}
                    style={styles.actionBtn}
                  >
                    <Check color={colors.primary} size={14} />
                  </Pressable>
                  <Pressable
                    onPress={cancelRename}
                    disabled={isSwitchingThread}
                    hitSlop={8}
                    style={styles.actionBtn}
                  >
                    <X color={colors.muted} size={14} />
                  </Pressable>
                </>
              ) : (
                <Pressable
                  onPress={() => startRename(thread.id, thread.name)}
                  disabled={isSwitchingThread}
                  hitSlop={8}
                  style={styles.actionBtn}
                >
                  <Pencil color={colors.muted} size={14} />
                </Pressable>
              )}
              <Pressable
                onPress={() => onDeleteThread(thread.id)}
                disabled={isSwitchingThread}
                hitSlop={8}
                style={styles.deleteBtn}
              >
                <Trash2 color={colors.muted} size={14} />
              </Pressable>
            </Pressable>
          );
        })}
      </ScrollView>

      {/* ── Account section ── */}
      <View style={[styles.accountSection, { borderTopColor: colors.border }]}>
        {/* Pop-up account menu (appears above user row) */}
        {accountMenuOpen && (
          <>
            {/* Transparent overlay to dismiss */}
            <Pressable
              style={StyleSheet.absoluteFill}
              onPress={() => setAccountMenuOpen(false)}
            />
            <View style={[styles.accountMenu, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <Pressable
                onPress={() => setAccountMenuOpen(false)}
                style={styles.accountMenuClose}
                hitSlop={10}
              >
                <X color={colors.muted} size={14} />
              </Pressable>
              <Pressable
                style={styles.accountMenuItem}
                onPress={() => {
                  setAccountMenuOpen(false);
                  onOpenProfile();
                }}
              >
                <User color={colors.text} size={15} />
                <Text style={[styles.accountMenuText, { color: colors.text, fontSize: getFontSize(14, largeText) }]}>
                  Profile
                </Text>
              </Pressable>
              <Pressable
                style={styles.accountMenuItem}
                onPress={() => {
                  setAccountMenuOpen(false);
                  onOpenSettings();
                }}
              >
                <Settings color={colors.text} size={15} />
                <Text style={[styles.accountMenuText, { color: colors.text, fontSize: getFontSize(14, largeText) }]}>
                  Settings
                </Text>
              </Pressable>
              <View style={[styles.accountMenuDivider, { backgroundColor: colors.border }]} />
              <Pressable
                style={styles.accountMenuItem}
                onPress={() => {
                  setAccountMenuOpen(false);
                  onLogout();
                }}
              >
                <LogOut color={colors.primary} size={15} />
                <Text style={[styles.accountMenuText, { color: colors.primary, fontSize: getFontSize(14, largeText) }]}>
                  Log out
                </Text>
              </Pressable>
            </View>
          </>
        )}

        {/* User row */}
        <Pressable
          onPress={() => setAccountMenuOpen((p) => !p)}
          style={({ pressed }) => [
            styles.userRow,
            { backgroundColor: pressed ? colors.surface : "transparent" },
          ]}
        >
          <View style={[styles.userAvatar, { backgroundColor: colors.primary }]}>
            <Text style={[styles.userAvatarText, { fontSize: getFontSize(15, largeText) }]}>
              {userInitial}
            </Text>
          </View>
          <View style={styles.userMeta}>
            <Text
              style={[styles.userName, { color: colors.text, fontSize: getFontSize(13, largeText) }]}
              numberOfLines={1}
            >
              {userDisplayName}
            </Text>
            <Text style={[styles.userPlan, { color: colors.muted, fontSize: getFontSize(11, largeText) }]}>
              {planLabel ?? "Free"}
            </Text>
          </View>
          <ChevronUp
            color={colors.muted}
            size={16}
            style={{ transform: [{ rotate: accountMenuOpen ? "180deg" : "0deg" }] }}
          />
        </Pressable>
      </View>
    </View>
  );
}

export default function ChatSidebar({
  visible,
  threads,
  activeThreadId,
  onSelectThread,
  onNewThread,
  onDeleteThread,
  onRenameThread,
  onClose,
  translateX,
  isCreatingThread = false,
  isSwitchingThread = false,
  userInitial,
  userDisplayName,
  planLabel,
  onOpenProfile,
  onOpenSettings,
  onLogout,
  persistentMode = false,
}: Props) {
  const { themeMode } = useAppSettings();
  const colors = palette[themeMode];

  const contentProps = {
    threads,
    activeThreadId,
    onSelectThread,
    onNewThread,
    onDeleteThread,
    onRenameThread,
    onClose,
    isCreatingThread,
    isSwitchingThread,
    userInitial,
    userDisplayName,
    planLabel,
    onOpenProfile,
    onOpenSettings,
    onLogout,
    persistentMode,
  };

  // Persistent mode: render as a plain side column (web wide viewport)
  if (persistentMode) {
    return (
      <View style={[styles.panelPersistent, { backgroundColor: colors.card, borderRightColor: colors.border }]}>
        <PanelContent {...contentProps} />
      </View>
    );
  }

  // Overlay mode: slide-in from left with dimmed backdrop
  if (!visible) return null;

  return (
    <View style={[StyleSheet.absoluteFill, { zIndex: 100 }]} pointerEvents="box-none">
      {/* Dimmed backdrop */}
      <TouchableWithoutFeedback onPress={onClose}>
        <Animated.View
          style={[
            StyleSheet.absoluteFill,
            styles.backdrop,
            {
              opacity: translateX.interpolate({
                inputRange: [-280, 0],
                outputRange: [0, 0.45],
              }),
            },
          ]}
        />
      </TouchableWithoutFeedback>

      {/* Sliding panel */}
      <Animated.View
        style={[
          styles.panel,
          { backgroundColor: colors.card, borderRightColor: colors.border },
          { transform: [{ translateX }] },
        ]}
      >
        <PanelContent {...contentProps} />
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  backdrop: { backgroundColor: "#000" },
  panel: {
    position: "absolute",
    left: 0,
    top: 0,
    bottom: 0,
    width: 280,
    borderRightWidth: 1,
    shadowColor: "#000",
    shadowOpacity: 0.15,
    shadowRadius: 16,
    shadowOffset: { width: 4, height: 0 },
    elevation: 10,
  },
  panelPersistent: {
    width: 280,
    borderRightWidth: 1,
  },
  panelInner: {
    flex: 1,
  },
  sidebarHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 18,
    paddingBottom: 16,
    borderBottomWidth: 1,
  },
  sidebarTitle: { fontWeight: "900" },
  closeBtn: { padding: 4 },
  newChatBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    margin: 14,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  newChatText: { color: "#fff", fontWeight: "700" },
  threadList: { flex: 1, paddingHorizontal: 8 },
  emptyText: { textAlign: "center", marginTop: 24, paddingHorizontal: 12 },
  threadItem: {
    flexDirection: "row",
    alignItems: "center",
    borderRadius: 10,
    paddingHorizontal: 10,
    paddingVertical: 10,
    marginBottom: 2,
    borderWidth: 1,
    gap: 8,
  },
  threadIcon: { flexShrink: 0 },
  threadInfo: { flex: 1, minWidth: 0 },
  threadName: { fontWeight: "600", marginBottom: 2 },
  threadPreview: { lineHeight: 15 },
  renameInput: {
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 5,
  },
  actionBtn: { padding: 4, flexShrink: 0 },
  deleteBtn: { padding: 4, flexShrink: 0 },

  // Account section
  accountSection: {
    borderTopWidth: 1,
    position: "relative",
  },
  accountMenu: {
    borderTopLeftRadius: 14,
    borderTopRightRadius: 14,
    borderWidth: 1,
    paddingVertical: 6,
    marginHorizontal: 8,
    marginBottom: 4,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: -4 },
    elevation: 8,
  },
  accountMenuItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingHorizontal: 14,
    paddingVertical: 11,
  },
  accountMenuText: { fontWeight: "600" },
  accountMenuClose: {
    position: "absolute",
    top: 8,
    right: 10,
    padding: 4,
    zIndex: 1,
  },
  accountMenuDivider: { height: 1, marginHorizontal: 10, marginVertical: 4 },
  userRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingHorizontal: 12,
    paddingVertical: 12,
    borderRadius: 0,
  },
  userAvatar: {
    width: 34,
    height: 34,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  userAvatarText: { color: "#fff", fontWeight: "800" },
  userMeta: { flex: 1, minWidth: 0 },
  userName: { fontWeight: "700", marginBottom: 1 },
  userPlan: { lineHeight: 14 },
});
