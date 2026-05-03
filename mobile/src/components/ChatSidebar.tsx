import { MessageSquare, Plus, Trash2, X } from "lucide-react-native";
import React from "react";
import {
  Animated,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
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
  onClose: () => void;
  translateX: Animated.Value;
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

export default function ChatSidebar({
  visible,
  threads,
  activeThreadId,
  onSelectThread,
  onNewThread,
  onDeleteThread,
  onClose,
  translateX,
}: Props) {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];

  if (!visible) return null;

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="box-none">
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

      {/* Sidebar panel */}
      <Animated.View
        style={[
          styles.panel,
          { backgroundColor: colors.card, borderRightColor: colors.border },
          { transform: [{ translateX }] },
        ]}
      >
        {/* Header */}
        <View style={[styles.sidebarHeader, { borderBottomColor: colors.border }]}>
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
          style={[styles.newChatBtn, { backgroundColor: colors.primary }]}
        >
          <Plus color="#fff" size={16} />
          <Text style={[styles.newChatText, { fontSize: getFontSize(14, largeText) }]}>
            New Chat
          </Text>
        </Pressable>

        {/* Thread list */}
        <ScrollView
          style={styles.threadList}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{ paddingBottom: 20 }}
        >
          {threads.length === 0 && (
            <Text style={[styles.emptyText, { color: colors.muted, fontSize: getFontSize(13, largeText) }]}>
              No conversations yet
            </Text>
          )}
          {threads.map((thread) => {
            const isActive = thread.id === activeThreadId;
            return (
              <Pressable
                key={thread.id}
                onPress={() => onSelectThread(thread.id)}
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
                </View>
                <Pressable
                  onPress={() => onDeleteThread(thread.id)}
                  hitSlop={8}
                  style={styles.deleteBtn}
                >
                  <Trash2 color={colors.muted} size={14} />
                </Pressable>
              </Pressable>
            );
          })}
        </ScrollView>
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
  sidebarHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 18,
    paddingTop: 56,
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
  deleteBtn: { padding: 4, flexShrink: 0 },
});
