import { Clock, MessageSquare, Trash2, X } from "lucide-react-native";
import React from "react";
import {
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { getFontSize, palette } from "../constants/theme";
import { useAppSettings } from "../context/AppSettingsContext";

export type ThreadItem = {
  id: string;
  name: string;
  preview: string;
  updatedAt: number;
};

type Props = {
  visible: boolean;
  onClose: () => void;
  onOpenThread: (chatId: string) => void;
  onDeleteThread: (chatId: string) => void;
  threads: ThreadItem[];
  userInitial: string;
  userDisplayName: string;
  userEmail: string;
  isGuest: boolean;
};

function formatDate(ts: number) {
  return new Date(ts).toLocaleDateString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function ProfileModal({
  visible,
  onClose,
  onOpenThread,
  onDeleteThread,
  threads,
  userInitial,
  userDisplayName,
  userEmail,
  isGuest,
}: Props) {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];

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
              Profile
            </Text>
            <Pressable onPress={onClose} style={styles.closeBtn} hitSlop={10}>
              <X color={colors.text} size={22} />
            </Pressable>
          </View>

          <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scroll}>
            {/* User card */}
            <View style={[styles.userCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <View style={[styles.avatarCircle, { backgroundColor: colors.primary }]}>
                <Text style={[styles.avatarText, { fontSize: getFontSize(26, largeText) }]}>
                  {userInitial}
                </Text>
              </View>
              <View style={styles.userInfo}>
                <Text style={[styles.userName, { color: colors.text, fontSize: getFontSize(17, largeText) }]}>
                  {userDisplayName}
                </Text>
                <Text style={[styles.userEmail, { color: colors.muted, fontSize: getFontSize(13, largeText) }]}>
                  {userEmail}
                </Text>
              </View>
              <View style={[styles.badge, { backgroundColor: colors.primarySoft }]}>
                <Text style={[styles.badgeText, { color: colors.primary, fontSize: getFontSize(11, largeText) }]}>
                  {isGuest ? "Guest" : "La Trobe"}
                </Text>
              </View>
            </View>

            {/* Chat history */}
            <Text style={[styles.sectionLabel, { color: colors.muted, fontSize: getFontSize(11, largeText) }]}>
              RECENT CHATS
            </Text>
            <View style={[styles.section, { backgroundColor: colors.card, borderColor: colors.border }]}>
              {threads.length === 0 ? (
                <View style={styles.emptyRow}>
                  <Clock color={colors.muted} size={18} />
                  <Text style={[styles.emptyText, { color: colors.muted, fontSize: getFontSize(13, largeText) }]}>
                    No conversations yet
                  </Text>
                </View>
              ) : (
                threads.slice(0, 8).map((thread, i) => (
                  <View
                    key={thread.id}
                    style={[
                      styles.threadRow,
                      i < Math.min(threads.length, 8) - 1 && { borderBottomWidth: 1, borderBottomColor: colors.border },
                    ]}
                  >
                    <View style={[styles.threadDot, { backgroundColor: colors.primarySoft }]}>
                      <MessageSquare color={colors.primary} size={13} />
                    </View>
                    <Pressable
                      style={styles.threadInfo}
                      onPress={() => {
                        onClose();
                        onOpenThread(thread.id);
                      }}
                    >
                      <Text
                        style={[styles.threadName, { color: colors.text, fontSize: getFontSize(14, largeText) }]}
                        numberOfLines={1}
                      >
                        {thread.name}
                      </Text>
                      <Text
                        style={[styles.threadMeta, { color: colors.muted, fontSize: getFontSize(11, largeText) }]}
                        numberOfLines={1}
                      >
                        {formatDate(thread.updatedAt)}
                        {thread.preview ? ` · ${thread.preview.slice(0, 40)}` : ""}
                      </Text>
                    </Pressable>
                    <Pressable
                      onPress={() => onDeleteThread(thread.id)}
                      hitSlop={10}
                      style={styles.deleteBtn}
                    >
                      <Trash2 color={colors.muted} size={15} />
                    </Pressable>
                  </View>
                ))
              )}
            </View>

            <Text style={[styles.footer, { color: colors.muted, fontSize: getFontSize(11, largeText) }]}>
              Campus-Aware AI · Cisco – La Trobe Centre for AI & IoT{"\n"}v1.0.0
            </Text>
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
    maxHeight: "88%",
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
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 32,
  },
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
    width: 50,
    height: 50,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  avatarText: { color: "#fff", fontWeight: "900" },
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
  emptyRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingHorizontal: 16,
    paddingVertical: 18,
  },
  emptyText: {},
  threadRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 14,
    paddingVertical: 11,
    gap: 12,
  },
  threadDot: {
    width: 28,
    height: 28,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  threadInfo: { flex: 1, minWidth: 0 },
  threadName: { fontWeight: "600", marginBottom: 2 },
  threadMeta: { lineHeight: 15 },
  deleteBtn: { padding: 4, flexShrink: 0 },
  footer: {
    textAlign: "center",
    lineHeight: 18,
  },
});
