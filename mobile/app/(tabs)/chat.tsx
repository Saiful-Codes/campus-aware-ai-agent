import AsyncStorage from "@react-native-async-storage/async-storage";
import * as DocumentPicker from "expo-document-picker";
import { router, useLocalSearchParams } from "expo-router";
import { Menu, Plus, RefreshCw, Send, X } from "lucide-react-native";
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Alert,
  Animated,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import ChatBubble from "../../src/components/ChatBubble";
import ChatSidebar, { ChatThread } from "../../src/components/ChatSidebar";
import { getFontSize, palette } from "../../src/constants/theme";
import { useAppSettings } from "../../src/context/AppSettingsContext";
import { useAuth } from "../../src/context/AuthContext";
import {
  appendChatMessage,
  createChatThread,
  deleteChatThread,
  subscribeChatMessages,
  subscribeChatThreads,
  updateChatMetadata,
} from "../../src/lib/chatThreads";

// ── Types ────────────────────────────────────────────────────────────────────

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  streaming?: boolean;
  isError?: boolean;
};

// ── Storage keys ─────────────────────────────────────────────────────────────

const THREADS_KEY = "campus_ai_threads_v2";
const ACTIVE_THREAD_KEY = "campus_ai_active_thread";

// ── Helpers ───────────────────────────────────────────────────────────────────

function generateId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

function threadName(firstMessage: string): string {
  const clean = firstMessage.replace(/[^\w\s]/g, "").trim();
  return clean.length > 36 ? clean.slice(0, 33) + "…" : clean || "New Chat";
}

function threadPreview(messages: Message[]): string {
  const last = [...messages].reverse().find((m) => m.role === "assistant");
  if (!last) return "";
  return last.text.replace(/[#*`>\n]/g, " ").replace(/\s+/g, " ").trim().slice(0, 50);
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function ChatScreen() {
  const params = useLocalSearchParams<{ chatId?: string }>();
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];
  const { user, isGuest } = useAuth();
  const isAuthenticatedUser = !!user?.uid && !isGuest;

  // ── Thread state
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string>("");
  const [threadMessages, setThreadMessages] = useState<Record<string, Message[]>>({});

  // ── UI state
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isCreatingThread, setIsCreatingThread] = useState(false);
  const [isSwitchingThread, setIsSwitchingThread] = useState(false);
  const [attachedFileName, setAttachedFileName] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [retryMessage, setRetryMessage] = useState<string | null>(null);

  const listRef = useRef<FlatList<Message>>(null);
  const sidebarAnim = useRef(new Animated.Value(-280)).current;

  const activeMessages: Message[] = threadMessages[activeThreadId] ?? [];

  const canSend = useMemo(
    () => (input.trim().length > 0 || !!attachedFileName) && !isLoading && !isSwitchingThread,
    [input, attachedFileName, isLoading, isSwitchingThread]
  );

  // ── Load threads ──────────────────────────────────────────────────────────

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
          console.log("Failed to subscribe threads", error);
        }
      );

      return unsubscribe;
    }

    const load = async () => {
      try {
        const [rawThreads, rawMessages, rawActive] = await Promise.all([
          AsyncStorage.getItem(THREADS_KEY),
          AsyncStorage.getItem(`${THREADS_KEY}_messages`),
          AsyncStorage.getItem(ACTIVE_THREAD_KEY),
        ]);

        let loadedThreads: ChatThread[] = rawThreads ? JSON.parse(rawThreads) : [];
        const loadedMessages: Record<string, Message[]> = rawMessages
          ? JSON.parse(rawMessages)
          : {};

        if (loadedThreads.length === 0) {
          const id = generateId();
          loadedThreads = [{ id, name: "New Chat", preview: "", updatedAt: Date.now() }];
          loadedMessages[id] = [];
        }

        const activeId =
          rawActive && loadedThreads.find((t) => t.id === rawActive)
            ? rawActive
            : loadedThreads[0].id;

        setThreads(loadedThreads);
        setThreadMessages(loadedMessages);
        setActiveThreadId(activeId);
      } catch (e) {
        console.log("Failed to load threads", e);
      }
    };
    load();
  }, [isAuthenticatedUser, user?.uid]);

  // Keep route param chatId in sync with active thread.
  useEffect(() => {
    if (!threads.length) {
      setActiveThreadId("");
      return;
    }

    const routeChatId = params.chatId;

    if (routeChatId && threads.some((t) => t.id === routeChatId)) {
      if (activeThreadId !== routeChatId) {
        setActiveThreadId(routeChatId);
      }
      return;
    }

    if (!activeThreadId || !threads.some((t) => t.id === activeThreadId)) {
      const fallbackId = threads[0].id;
      setActiveThreadId(fallbackId);
      if (isAuthenticatedUser) {
        router.replace({ pathname: "/chat", params: { chatId: fallbackId } });
      }
    }
  }, [threads, params.chatId, activeThreadId, isAuthenticatedUser]);

  // Load active thread messages from Firestore for authenticated users.
  useEffect(() => {
    if (!isAuthenticatedUser || !user?.uid || !activeThreadId) return;

    setIsSwitchingThread(true);
    const unsubscribe = subscribeChatMessages(
      user.uid,
      activeThreadId,
      (rows) => {
        const mapped: Message[] = rows.map((m) => ({
          id: m.id,
          role: m.role,
          text: m.content,
          streaming: false,
          isError: false,
        }));

        setThreadMessages((prev) => ({ ...prev, [activeThreadId]: mapped }));
        setIsSwitchingThread(false);
      },
      (error) => {
        console.log("Failed to subscribe messages", error);
        setIsSwitchingThread(false);
      }
    );

    return unsubscribe;
  }, [isAuthenticatedUser, user?.uid, activeThreadId]);

  // Reset when auth changes
  useEffect(() => {
    setInput("");
    setAttachedFileName(null);
    setIsLoading(false);
  }, [user, isGuest]);

  // ── Persist threads ───────────────────────────────────────────────────────

  const persist = useCallback(
    async (updatedThreads: ChatThread[], updatedMessages: Record<string, Message[]>) => {
      if (isAuthenticatedUser) return;
      try {
        await Promise.all([
          AsyncStorage.setItem(THREADS_KEY, JSON.stringify(updatedThreads)),
          AsyncStorage.setItem(`${THREADS_KEY}_messages`, JSON.stringify(updatedMessages)),
        ]);
      } catch (e) {
        console.log("Failed to persist threads", e);
      }
    },
    [isAuthenticatedUser]
  );

  const persistActiveId = useCallback(async (id: string) => {
    if (isAuthenticatedUser) return;
    try {
      await AsyncStorage.setItem(ACTIVE_THREAD_KEY, id);
    } catch { }
  }, [isAuthenticatedUser]);

  // ── Thread operations ─────────────────────────────────────────────────────

  const createThread = useCallback(async (): Promise<string | null> => {
    if (isCreatingThread) return null;

    setIsCreatingThread(true);

    if (isAuthenticatedUser && user?.uid) {
      try {
        const id = await createChatThread(user.uid);
        setThreadMessages((prev) => ({ ...prev, [id]: [] }));
        setActiveThreadId(id);
        setSidebarOpen(false);
        closeSidebar();
        router.replace({ pathname: "/chat", params: { chatId: id } });
        return id;
      } catch (error) {
        console.log("Failed to create chat", error);
        Alert.alert("Could not create chat", "Please try again.");
        return null;
      } finally {
        setIsCreatingThread(false);
      }
    }

    const id = generateId();
    const newThread: ChatThread = { id, name: "New Chat", preview: "", updatedAt: Date.now() };
    const updatedThreads = [newThread, ...threads];
    const updatedMessages = { ...threadMessages, [id]: [] };
    setThreads(updatedThreads);
    setThreadMessages(updatedMessages);
    setActiveThreadId(id);
    setSidebarOpen(false);
    closeSidebar();
    persist(updatedThreads, updatedMessages);
    persistActiveId(id);
    setIsCreatingThread(false);
    return id;
  }, [
    isCreatingThread,
    isAuthenticatedUser,
    user?.uid,
    threads,
    threadMessages,
    persist,
    persistActiveId,
  ]);

  const selectThread = useCallback(
    (id: string) => {
      if (id === activeThreadId) {
        closeSidebar();
        return;
      }

      setIsSwitchingThread(true);
      setActiveThreadId(id);
      setInput("");
      setAttachedFileName(null);
      setRetryMessage(null);

      if (isAuthenticatedUser) {
        router.replace({ pathname: "/chat", params: { chatId: id } });
      } else {
        setIsSwitchingThread(false);
      }

      closeSidebar();
      persistActiveId(id);
    },
    [activeThreadId, isAuthenticatedUser, persistActiveId]
  );

  const deleteThread = useCallback(
    async (id: string) => {
      if (isAuthenticatedUser && user?.uid) {
        try {
          await deleteChatThread(user.uid, id);

          const remaining = threads.filter((t) => t.id !== id);
          if (id === activeThreadId) {
            const nextId = remaining[0]?.id ?? "";
            setActiveThreadId(nextId);
            if (nextId) {
              router.replace({ pathname: "/chat", params: { chatId: nextId } });
            }
          }
        } catch (error) {
          console.log("Delete thread failed", error);
          Alert.alert("Could not delete chat", "Please try again.");
        }
        return;
      }

      const updatedThreads = threads.filter((t) => t.id !== id);
      const updatedMessages = { ...threadMessages };
      delete updatedMessages[id];

      if (updatedThreads.length === 0) {
        const newId = generateId();
        updatedThreads.push({ id: newId, name: "New Chat", preview: "", updatedAt: Date.now() });
        updatedMessages[newId] = [];
        setActiveThreadId(newId);
        persistActiveId(newId);
      } else if (id === activeThreadId) {
        setActiveThreadId(updatedThreads[0].id);
        persistActiveId(updatedThreads[0].id);
      }

      setThreads(updatedThreads);
      setThreadMessages(updatedMessages);
      persist(updatedThreads, updatedMessages);
    },
    [threads, threadMessages, activeThreadId, isAuthenticatedUser, user?.uid, persist, persistActiveId]
  );

  // ── Sidebar animation ─────────────────────────────────────────────────────

  const openSidebar = () => {
    setSidebarOpen(true);
    Animated.spring(sidebarAnim, {
      toValue: 0,
      useNativeDriver: true,
      tension: 80,
      friction: 12,
    }).start();
  };

  const closeSidebar = () => {
    Animated.spring(sidebarAnim, {
      toValue: -280,
      useNativeDriver: true,
      tension: 80,
      friction: 12,
    }).start(() => setSidebarOpen(false));
  };

  // ── Message helpers ───────────────────────────────────────────────────────

  const scrollToBottom = () => {
    setTimeout(() => listRef.current?.scrollToEnd({ animated: true }), 80);
  };

  const updateMessages = useCallback(
    (threadId: string, updater: (prev: Message[]) => Message[]) => {
      setThreadMessages((prev) => {
        const updated = { ...prev, [threadId]: updater(prev[threadId] ?? []) };
        return updated;
      });
    },
    []
  );

  // ── Send ──────────────────────────────────────────────────────────────────

  const handleSend = async (overrideText?: string) => {
    if (isSwitchingThread) return;

    const textToSend = overrideText ?? input.trim();
    if (!textToSend && !attachedFileName) return;
    if (isLoading) return;

    let targetThreadId = activeThreadId;
    if (!targetThreadId) {
      const createdId = await createThread();
      if (!createdId) return;
      targetThreadId = createdId;
    }

    setRetryMessage(null);

    const userMessage: Message = {
      id: `${Date.now()}-user`,
      role: "user",
      text: textToSend || `Uploaded document: ${attachedFileName}`,
    };

    // Auto-name the thread from first message
    const currentMessages = threadMessages[targetThreadId] ?? [];
    const isFirstMessage = currentMessages.filter((m) => m.role === "user").length === 0;

    updateMessages(targetThreadId, (prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    scrollToBottom();

    // Placeholder
    const assistantId = `${Date.now()}-assistant`;
    updateMessages(targetThreadId, (prev) => [
      ...prev,
      { id: assistantId, role: "assistant", text: "…", streaming: true },
    ]);
    scrollToBottom();

    const normalizedTitle = isFirstMessage ? threadName(textToSend) : undefined;

    if (isAuthenticatedUser && user?.uid) {
      try {
        await appendChatMessage(user.uid, targetThreadId, {
          role: "user",
          content: userMessage.text,
        });
        await updateChatMetadata(user.uid, targetThreadId, {
          title: normalizedTitle,
          lastMessage: userMessage.text,
          messageIncrement: 1,
        });
      } catch (error) {
        console.log("Failed to persist user message", error);
      }
    }

    try {
      let responseText = "";
      let isRagUsed = false;
      let backendStatus: string | undefined;

      // Try RAG first
      try {
        const ragRes = await fetch(`${process.env.EXPO_PUBLIC_API_BASE_URL}/rag/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: textToSend }),
        });

        if (!ragRes.ok) throw new Error(`HTTP ${ragRes.status}`);

        const ragData = await ragRes.json();
        const ragAnswer = ragData.response;
        backendStatus = ragData.status;

        if (ragAnswer) {
          const lower = ragAnswer.toLowerCase();
          const isBadAnswer =
            lower.includes("i don't know") ||
            lower.includes("don't have enough information") ||
            lower.includes("not enough information") ||
            lower.includes("cannot answer") ||
            lower.includes("no relevant information");

          if (!isBadAnswer && ragAnswer.length > 20) {
            responseText = ragAnswer;
            isRagUsed = true;
          }
        }
      } catch {
        // RAG failed — fall through to standard chat
      }

      // Fallback
      if (!responseText) {
        const response = await fetch(`${process.env.EXPO_PUBLIC_API_BASE_URL}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: textToSend }),
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        backendStatus = data.status;
        responseText =
          data.response ?? data.answer ?? data.message ?? "Sorry, I could not generate a response.";
      }

      const finalText = isRagUsed ? `📄 *From campus documents*\n\n${responseText}` : responseText;

      updateMessages(targetThreadId, (prev) =>
        prev.map((m) =>
          m.id === assistantId ? { ...m, text: finalText, streaming: true } : m
        )
      );

      if (isAuthenticatedUser && user?.uid) {
        try {
          const usedDatabase =
            backendStatus === "sensor_response" ||
            backendStatus === "text_to_flux_response";

          await appendChatMessage(user.uid, targetThreadId, {
            role: "assistant",
            content: finalText,
            intent: backendStatus,
            usedDatabase,
            usedGemini: true,
          });
          await updateChatMetadata(user.uid, targetThreadId, {
            title: normalizedTitle,
            lastMessage: finalText,
            messageIncrement: 1,
          });
        } catch (error) {
          console.log("Failed to persist assistant message", error);
        }
      }

      // Update thread metadata
      const nameForThread = normalizedTitle;
      setThreads((prev) => {
        const updated = prev.map((t) =>
          t.id === targetThreadId
            ? {
              ...t,
              name: nameForThread ?? t.name,
              preview: finalText.replace(/[#*`>\n]/g, " ").replace(/\s+/g, " ").trim().slice(0, 50),
              updatedAt: Date.now(),
            }
            : t
        );
        // Re-sort: most recently updated first
        return [...updated].sort((a, b) => b.updatedAt - a.updatedAt);
      });

      scrollToBottom();
    } catch {
      const errorText = "Something went wrong. Please try again.";
      updateMessages(targetThreadId, (prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, text: errorText, streaming: false, isError: true }
            : m
        )
      );
      setRetryMessage(textToSend);
    } finally {
      setAttachedFileName(null);
      setIsLoading(false);
    }
  };

  const handleStreamComplete = (msgId: string) => {
    if (isAuthenticatedUser) return;

    setThreadMessages((prev) => {
      const msgs = prev[activeThreadId] ?? [];
      const updated = msgs.map((m) => (m.id === msgId ? { ...m, streaming: false } : m));
      const newState = { ...prev, [activeThreadId]: updated };
      // Persist after stream completes
      persist(
        threads.map((t) =>
          t.id === activeThreadId
            ? { ...t, preview: threadPreview(updated) }
            : t
        ),
        newState
      );
      return newState;
    });
  };

  const handlePickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: "application/pdf",
        multiple: false,
        copyToCacheDirectory: true,
      });
      if (!result.canceled && result.assets?.length > 0) {
        setAttachedFileName(result.assets[0].name);
      }
    } catch (e) {
      console.log("Document picker error", e);
    }
  };

  const currentThreadName =
    threads.find((t) => t.id === activeThreadId)?.name ?? "Campus AI";

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.background }]}>
      <KeyboardAvoidingView
        style={styles.safe}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <View style={styles.container}>

          {/* ── Header ── */}
          <View style={[styles.header, { borderBottomColor: colors.border }]}>
            <Pressable
              onPress={openSidebar}
              style={[styles.iconBtn, { backgroundColor: colors.surface, borderColor: colors.border }]}
            >
              <Menu color={colors.text} size={20} />
            </Pressable>

            <Text
              style={[styles.headerTitle, { color: colors.text, fontSize: getFontSize(14, largeText) }]}
              numberOfLines={1}
            >
              {currentThreadName}
            </Text>
          </View>

          {isSwitchingThread && (
            <Text style={[styles.switchingText, { color: colors.muted, fontSize: getFontSize(12, largeText) }]}>
              Loading chat...
            </Text>
          )}

          {/* ── Empty state ── */}
          {activeMessages.length === 0 && (
            <View style={styles.emptyState}>
              <Text style={[styles.emptyTitle, { color: colors.primary, fontSize: getFontSize(22, largeText) }]}>
                Campus AI
              </Text>
              <Text style={[styles.emptySubtitle, { color: colors.muted, fontSize: getFontSize(13, largeText) }]}>
                Ask me about rooms, campus information, or upload a PDF document.
              </Text>
            </View>
          )}

          {/* ── Message list ── */}
          <FlatList
            ref={listRef}
            data={activeMessages}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <ChatBubble
                role={item.role}
                text={item.text}
                streaming={item.streaming}
                onStreamComplete={() => handleStreamComplete(item.id)}
              />
            )}
            contentContainerStyle={styles.chatList}
            showsVerticalScrollIndicator={false}
            onContentSizeChange={scrollToBottom}
          />

          {/* ── Retry banner ── */}
          {retryMessage && !isLoading && (
            <Pressable
              onPress={() => handleSend(retryMessage)}
              style={[styles.retryBanner, { backgroundColor: colors.primarySoft, borderColor: colors.primary }]}
            >
              <RefreshCw color={colors.primary} size={14} />
              <Text style={[styles.retryText, { color: colors.primary, fontSize: getFontSize(13, largeText) }]}>
                Tap to retry
              </Text>
            </Pressable>
          )}

          {/* ── Attachment chip ── */}
          {attachedFileName && (
            <View style={[styles.attachmentChip, { backgroundColor: colors.primarySoft, borderColor: colors.border }]}>
              <Text
                style={[styles.attachmentText, { color: colors.text, fontSize: getFontSize(13, largeText) }]}
                numberOfLines={1}
              >
                {attachedFileName}
              </Text>
              <Pressable onPress={() => setAttachedFileName(null)} hitSlop={8}>
                <X color={colors.text} size={16} />
              </Pressable>
            </View>
          )}

          {/* ── Input bar ── */}
          <View style={[styles.inputContainer, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <Pressable
              onPress={handlePickDocument}
              style={[styles.iconButton, { backgroundColor: colors.surface2, borderColor: colors.border }]}
            >
              <Plus color={colors.text} size={18} />
            </Pressable>

            <TextInput
              value={input}
              onChangeText={setInput}
              placeholder="Ask a question..."
              placeholderTextColor={colors.muted}
              style={[styles.input, { color: colors.text, fontSize: getFontSize(15, largeText) }]}
              multiline
              onSubmitEditing={() => handleSend()}
              submitBehavior="newline"
            />

            <Pressable
              onPress={() => handleSend()}
              disabled={!canSend}
              style={[styles.sendButton, { backgroundColor: colors.primary, opacity: canSend ? 1 : 0.4 }]}
            >
              <Send color={colors.white} size={18} />
            </Pressable>
          </View>
        </View>

        {/* ── Sidebar ── */}
        <ChatSidebar
          visible={sidebarOpen}
          threads={threads}
          activeThreadId={activeThreadId}
          onSelectThread={selectThread}
          onNewThread={() => {
            createThread();
          }}
          onDeleteThread={deleteThread}
          onClose={closeSidebar}
          translateX={sidebarAnim}
          isCreatingThread={isCreatingThread}
          isSwitchingThread={isSwitchingThread}
        />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  container: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 12,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 8,
    paddingBottom: 10,
    borderBottomWidth: 1,
    zIndex: 20,
  },
  headerTitle: { flex: 1, fontWeight: "700", textAlign: "left", marginLeft: 10 },
  iconBtn: {
    width: 40,
    height: 40,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
  },
  menuWrapper: { position: "relative", zIndex: 30 },
  menuDropdown: {
    position: "absolute",
    top: 48,
    right: 0,
    width: 190,
    borderRadius: 14,
    borderWidth: 1,
    paddingVertical: 6,
    zIndex: 999,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
    elevation: 6,
  },
  menuItem: { paddingHorizontal: 14, paddingVertical: 11 },
  menuText: { fontWeight: "500" },
  menuDivider: { height: 1, marginVertical: 4, marginHorizontal: 10 },
  emptyState: {
    flex: 0,
    alignItems: "flex-start",
    paddingTop: 20,
    paddingBottom: 16,
    paddingHorizontal: 4,
  },
  emptyTitle: { fontWeight: "800", marginBottom: 4, textAlign: "left" },
  emptySubtitle: { textAlign: "left", lineHeight: 20 },
  switchingText: {
    marginTop: 4,
    marginBottom: 8,
    paddingHorizontal: 4,
    fontWeight: "500",
  },
  chatList: {
    paddingTop: 8,
    paddingBottom: 12,
    flexGrow: 1,
  },
  retryBanner: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 10,
    marginBottom: 8,
  },
  retryText: { fontWeight: "600" },
  attachmentChip: {
    marginBottom: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 14,
    borderWidth: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 10,
  },
  attachmentText: { flex: 1, fontWeight: "600" },
  inputContainer: {
    borderRadius: 22,
    borderWidth: 1,
    padding: 10,
    flexDirection: "row",
    alignItems: "flex-end",
    gap: 10,
  },
  iconButton: {
    width: 42,
    height: 42,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
  },
  input: {
    flex: 1,
    minHeight: 42,
    maxHeight: 120,
    paddingTop: 10,
    paddingBottom: 10,
  },
  sendButton: {
    width: 42,
    height: 42,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
  },
});
