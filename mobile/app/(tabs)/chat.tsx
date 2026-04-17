import AsyncStorage from "@react-native-async-storage/async-storage";
import * as DocumentPicker from "expo-document-picker";
import { router } from "expo-router";
import { Menu, Plus, Send, X } from "lucide-react-native";
import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  TouchableWithoutFeedback,
  View,
} from "react-native";
import ChatBubble from "../../src/components/ChatBubble";
import { getFontSize, palette } from "../../src/constants/theme";
import { useAppSettings } from "../../src/context/AppSettingsContext";
import { useAuth } from "../../src/context/AuthContext";
import { db } from "../../src/lib/firebase";
import { addDoc, collection, getDocs, orderBy, query, Timestamp } from "firebase/firestore";

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  streaming?: boolean;
};

const RECENT_CHATS_KEY = "campus_ai_recent_chats";

// Suggested prompts shown on empty state
const SUGGESTED_PROMPTS = [
  "Is PW-202 usually stuffy in the afternoon?",
  "What's the CO₂ level in the library?",
  "Which rooms have high noise levels?",
  "Show me temperature trends today",
];

export default function ChatScreen() {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];
  const { logout, user, isGuest } = useAuth();

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [attachedFileName, setAttachedFileName] = useState<string | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [recentChats, setRecentChats] = useState<string[]>([]);

  const listRef = useRef<FlatList<Message>>(null);

  const canSend = useMemo(
    () => (input.trim().length > 0 || !!attachedFileName) && !isLoading,
    [input, attachedFileName, isLoading]
  );

  useEffect(() => {
    const loadRecentChats = async () => {
      try {
        const stored = await AsyncStorage.getItem(RECENT_CHATS_KEY);
        if (stored) setRecentChats(JSON.parse(stored));
      } catch (e) {
        console.log("Failed to load recent chats", e);
      }
    };
    loadRecentChats();
  }, []);

  useEffect(() => {
    setMessages([]);
    setInput("");
    setAttachedFileName(null);
    setIsLoading(false);
  }, [user, isGuest]);

  useEffect(() => {
    if (!user || isGuest) return;
    const loadChatHistory = async () => {
      try {
        const q = query(
          collection(db, "users", user.uid, "chats", "default", "messages"),
          orderBy("timestamp", "asc")
        );
        const querySnapshot = await getDocs(q);
        const loadedMessages = querySnapshot.docs.map((doc) => {
          const data = doc.data();
          return {
            id: doc.id,
            role: data.role,
            text: data.text,
          };
        });
        setMessages(loadedMessages);
      } catch (error) {
        console.log("Failed to load chat history", error);
      }
    };
    loadChatHistory();
  }, [user, isGuest]);

  const saveRecentChats = async (items: string[]) => {
    try {
      await AsyncStorage.setItem(RECENT_CHATS_KEY, JSON.stringify(items));
    } catch (e) {
      console.log("Failed to save recent chats", e);
    }
  };

  const addRecentChat = async (text: string) => {
    if (!text.trim()) return;
    const updated = [
      text.trim(),
      ...recentChats.filter((item) => item !== text.trim()),
    ].slice(0, 8);
    setRecentChats(updated);
    await saveRecentChats(updated);
  };

  const scrollToBottom = () => {
    setTimeout(() => {
      listRef.current?.scrollToEnd({ animated: true });
    }, 80);
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

  const handleNewChat = () => {
    setMessages([]);
    setInput("");
    setAttachedFileName(null);
    setIsLoading(false);
    setMenuOpen(false);
  };

  const handleSend = async (promptText?: string) => {
    const textToSend = promptText ?? input.trim();
    if (!textToSend && !attachedFileName) return;
    if (isLoading) return;

    const userMessage: Message = {
      id: `${Date.now()}-user`,
      role: "user",
      text: textToSend || `Uploaded document: ${attachedFileName}`,
    };

    setMessages((prev) => [...prev, userMessage]);
    if (user && !isGuest) {
      try {
        await addDoc(collection(db, "users", user.uid, "chats", "default", "messages"), {
          role: "user",
          text: userMessage.text,
          timestamp: Timestamp.now(),
        });
      } catch (error) {
        console.log("Failed to save user message", error);
      }
    }
    if (textToSend.trim()) await addRecentChat(textToSend.trim());

    setInput("");
    setMenuOpen(false);
    setIsLoading(true);
    scrollToBottom();

    // Add a placeholder streaming message immediately — shows cursor right away
    const assistantId = `${Date.now()}-assistant`;
    const placeholderMessage: Message = {
      id: assistantId,
      role: "assistant",
      text: "…",
      streaming: true,
    };
    setMessages((prev) => [...prev, placeholderMessage]);
    scrollToBottom();

    try {
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_API_BASE_URL}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: textToSend }),
        }
      );

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      const responseText =
        data.response ??
        data.answer ??
        data.message ??
        "Sorry, I could not generate a response.";

      // Replace placeholder with real text, still streaming (word-by-word will play)
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, text: responseText, streaming: true }
            : m
        )
      );
      if (user && !isGuest) {
        try {
          await addDoc(collection(db, "users", user.uid, "chats", "default", "messages"), {
            role: "assistant",
            text: responseText,
            timestamp: Timestamp.now(),
          });
        } catch (error) {
          console.log("Failed to save assistant message", error);
        }
      }
      scrollToBottom();
    } catch (e) {
      const errorText = "⚠️ Could not reach the backend. Please check your connection.";
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                text: errorText,
                streaming: true,
              }
            : m
        )
      );
      if (user && !isGuest) {
        try {
          await addDoc(collection(db, "users", user.uid, "chats", "default", "messages"), {
            role: "assistant",
            text: errorText,
            timestamp: Timestamp.now(),
          });
        } catch (error) {
          console.log("Failed to save assistant error message", error);
        }
      }
      console.log("Chat backend error", e);
    } finally {
      setAttachedFileName(null);
      setIsLoading(false);
    }
  };

  const handleStreamComplete = (msgId: string) => {
    // Mark streaming as done so cursor disappears
    setMessages((prev) =>
      prev.map((m) => (m.id === msgId ? { ...m, streaming: false } : m))
    );
  };

  const isEmpty = messages.length === 0;

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.background }]}>
      <KeyboardAvoidingView
        style={styles.safe}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <TouchableWithoutFeedback onPress={() => setMenuOpen(false)}>
          <View style={styles.container}>

            {/* ── Header ── */}
            <View style={styles.header}>
              <Text
                style={[
                  styles.headerTitle,
                  { color: colors.primary, fontSize: getFontSize(28, largeText) },
                ]}
              >
                Campus AI
              </Text>

              <View style={styles.menuWrapper}>
                <Pressable
                  onPress={() => setMenuOpen((prev) => !prev)}
                  style={[
                    styles.menuButton,
                    { backgroundColor: colors.surface, borderColor: colors.border },
                  ]}
                >
                  <Menu color={colors.text} size={20} />
                </Pressable>

                {menuOpen && (
                  <View
                    style={[
                      styles.menuDropdown,
                      { backgroundColor: colors.card, borderColor: colors.border },
                    ]}
                  >
                    <Pressable style={styles.menuItem} onPress={handleNewChat}>
                      <Text style={[styles.menuText, { color: colors.text, fontSize: getFontSize(14, largeText) }]}>
                        New Chat
                      </Text>
                    </Pressable>

                    <Pressable
                      style={styles.menuItem}
                      onPress={() => { setMenuOpen(false); router.push("/settings"); }}
                    >
                      <Text style={[styles.menuText, { color: colors.text, fontSize: getFontSize(14, largeText) }]}>
                        Settings
                      </Text>
                    </Pressable>

                    <View style={[styles.menuDivider, { backgroundColor: colors.border }]} />

                    <Pressable
                      style={styles.menuItem}
                      onPress={async () => {
                        setMenuOpen(false);
                        await logout();
                        setMessages([]);
                        router.replace("/login");
                      }}
                    >
                      <Text style={[styles.menuText, { color: colors.text, fontSize: getFontSize(14, largeText) }]}>
                        Log Out
                      </Text>
                    </Pressable>

                    <View style={[styles.menuDivider, { backgroundColor: colors.border }]} />

                    <Text style={[styles.menuSectionTitle, { color: colors.muted, fontSize: getFontSize(12, largeText) }]}>
                      Recent Chats
                    </Text>

                    {recentChats.length === 0 ? (
                      <Text style={[styles.menuEmptyText, { color: colors.muted, fontSize: getFontSize(13, largeText) }]}>
                        No recent chats
                      </Text>
                    ) : (
                      recentChats.map((chat, index) => (
                        <Pressable
                          key={`${chat}-${index}`}
                          style={styles.menuItem}
                          onPress={() => { setInput(chat); setMenuOpen(false); }}
                        >
                          <Text
                            style={[styles.menuText, { color: colors.text, fontSize: getFontSize(13, largeText) }]}
                            numberOfLines={1}
                          >
                            {chat}
                          </Text>
                        </Pressable>
                      ))
                    )}
                  </View>
                )}
              </View>
            </View>

            {/* ── Welcome box (always visible) ── */}
            <View style={[styles.welcomeBox, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <Text style={[styles.welcomeText, { color: colors.text, fontSize: getFontSize(15, largeText) }]}>
                Hi, I am Campus AI. Ask me about rooms, campus information, or uploaded PDF documents.
              </Text>
            </View>

            {/* ── Empty state: suggested prompts ── */}
            {isEmpty && (
              <View style={styles.suggestionsContainer}>
                <Text style={[styles.suggestionsLabel, { color: colors.muted, fontSize: getFontSize(12, largeText) }]}>
                  TRY ASKING
                </Text>
                <View style={styles.suggestionsGrid}>
                  {SUGGESTED_PROMPTS.map((prompt) => (
                    <Pressable
                      key={prompt}
                      style={[styles.suggestionChip, { backgroundColor: colors.surface, borderColor: colors.border }]}
                      onPress={() => handleSend(prompt)}
                    >
                      <Text
                        style={[styles.suggestionText, { color: colors.text, fontSize: getFontSize(13, largeText) }]}
                        numberOfLines={2}
                      >
                        {prompt}
                      </Text>
                    </Pressable>
                  ))}
                </View>
              </View>
            )}

            {/* ── Message list ── */}
            <FlatList
              ref={listRef}
              data={messages}
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

            {/* ── Attachment chip ── */}
            {attachedFileName && (
              <View style={[styles.attachmentChip, { backgroundColor: colors.primarySoft, borderColor: colors.border }]}>
                <Text
                  style={[styles.attachmentText, { color: colors.text, fontSize: getFontSize(13, largeText) }]}
                  numberOfLines={1}
                >
                  {attachedFileName}
                </Text>
                <Pressable onPress={() => setAttachedFileName(null)}>
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
                blurOnSubmit={false}
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
        </TouchableWithoutFeedback>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  container: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 12,
  },
  header: {
    marginBottom: 14,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    zIndex: 20,
  },
  headerTitle: { fontWeight: "900" },
  menuWrapper: { position: "relative", zIndex: 30 },
  menuButton: {
    width: 42,
    height: 42,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
  },
  menuDropdown: {
    position: "absolute",
    top: 50,
    right: 0,
    width: 250,
    borderRadius: 16,
    borderWidth: 1,
    paddingVertical: 8,
    zIndex: 999,
    shadowColor: "#000",
    shadowOpacity: 0.08,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
    elevation: 6,
  },
  menuItem: { paddingHorizontal: 14, paddingVertical: 10 },
  menuText: { fontWeight: "500" },
  menuDivider: { height: 1, marginVertical: 6, marginHorizontal: 12 },
  menuSectionTitle: {
    fontWeight: "700",
    paddingHorizontal: 14,
    paddingTop: 4,
    paddingBottom: 6,
    textTransform: "uppercase",
    letterSpacing: 0.6,
  },
  menuEmptyText: { paddingHorizontal: 14, paddingBottom: 8 },
  welcomeBox: {
    borderRadius: 20,
    borderWidth: 1,
    padding: 16,
    marginBottom: 14,
  },
  welcomeText: { fontWeight: "500", lineHeight: 22 },
  suggestionsContainer: { marginBottom: 10 },
  suggestionsLabel: {
    fontWeight: "700",
    letterSpacing: 0.8,
    marginBottom: 8,
    paddingHorizontal: 2,
  },
  suggestionsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  suggestionChip: {
    borderWidth: 1,
    borderRadius: 14,
    paddingHorizontal: 14,
    paddingVertical: 10,
    width: "47%",
  },
  suggestionText: {
    fontWeight: "500",
    lineHeight: 18,
  },
  chatList: {
    paddingTop: 8,
    paddingBottom: 12,
    flexGrow: 1,
  },
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
