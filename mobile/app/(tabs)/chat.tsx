import AsyncStorage from "@react-native-async-storage/async-storage";
import * as DocumentPicker from "expo-document-picker";
import { router } from "expo-router";
import { Menu, Plus, Send, X } from "lucide-react-native";
import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  ActivityIndicator,
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

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
};


const RECENT_CHATS_KEY = "campus_ai_recent_chats";

export default function ChatScreen() {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [attachedFileName, setAttachedFileName] = useState<string | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [recentChats, setRecentChats] = useState<string[]>([]);

  const listRef = useRef<FlatList<Message>>(null);

  const canSend = useMemo(
    () => input.trim().length > 0 || !!attachedFileName,
    [input, attachedFileName]
  );

  useEffect(() => {
    const loadRecentChats = async () => {
      try {
        const stored = await AsyncStorage.getItem(RECENT_CHATS_KEY);
        if (stored) {
          setRecentChats(JSON.parse(stored));
        }
      } catch (error) {
        console.log("Failed to load recent chats", error);
      }
    };

    loadRecentChats();
  }, []);

  const saveRecentChats = async (items: string[]) => {
    try {
      await AsyncStorage.setItem(RECENT_CHATS_KEY, JSON.stringify(items));
    } catch (error) {
      console.log("Failed to save recent chats", error);
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
    }, 100);
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
    } catch (error) {
      console.log("Document picker error", error);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setInput("");
    setAttachedFileName(null);
    setTyping(false);
    setMenuOpen(false);
  };

  const handleSend = async (promptText?: string) => {
    const textToSend = promptText ?? input.trim();

    if (!textToSend && !attachedFileName) return;

    const userMessage: Message = {
      id: `${Date.now()}-user`,
      role: "user",
      text: textToSend || `Uploaded document: ${attachedFileName}`,
    };

    setMessages((prev) => [...prev, userMessage]);

    if (textToSend.trim()) {
      await addRecentChat(textToSend.trim());
    }

    setInput("");
    setTyping(true);
    setMenuOpen(false);
    scrollToBottom();

    try {
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_API_BASE_URL}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ query: textToSend }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: `${Date.now()}-assistant`,
        role: "assistant",
        text:
          data.response ??
          data.answer ??
          data.message ??
          "Sorry, I could not generate a response.",
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const assistantMessage: Message = {
        id: `${Date.now()}-assistant`,
        role: "assistant",
        text: "Backend connection failed.",
      };

      setMessages((prev) => [...prev, assistantMessage]);
      console.log("Chat backend error", error);
    } finally {
      setTyping(false);
      setAttachedFileName(null);
      scrollToBottom();
    }
  };

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.background }]}>
      <KeyboardAvoidingView
        style={styles.safe}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <TouchableWithoutFeedback onPress={() => setMenuOpen(false)}>
          <View style={styles.container}>
            <View style={styles.header}>
              <Text
                style={[
                  styles.headerTitle,
                  {
                    color: colors.primary,
                    fontSize: getFontSize(28, largeText),
                  },
                ]}
              >
                Campus AI
              </Text>

              <View style={styles.menuWrapper}>
                <Pressable
                  onPress={() => setMenuOpen((prev) => !prev)}
                  style={[
                    styles.menuButton,
                    {
                      backgroundColor: colors.surface,
                      borderColor: colors.border,
                    },
                  ]}
                >
                  <Menu color={colors.text} size={20} />
                </Pressable>

                {menuOpen ? (
                  <View
                    style={[
                      styles.menuDropdown,
                      {
                        backgroundColor: colors.card,
                        borderColor: colors.border,
                      },
                    ]}
                  >
                    <Pressable style={styles.menuItem} onPress={handleNewChat}>
                      <Text
                        style={[
                          styles.menuText,
                          { color: colors.text, fontSize: getFontSize(14, largeText) },
                        ]}
                      >
                        New Chat
                      </Text>
                    </Pressable>

                    <Pressable
                      style={styles.menuItem}
                      onPress={() => {
                        setMenuOpen(false);
                        router.push("/settings");
                      }}
                    >
                      <Text
                        style={[
                          styles.menuText,
                          { color: colors.text, fontSize: getFontSize(14, largeText) },
                        ]}
                      >
                        Settings
                      </Text>
                    </Pressable>

                    <View
                      style={[
                        styles.menuDivider,
                        { backgroundColor: colors.border },
                      ]}
                    />

                    <Text
                      style={[
                        styles.menuSectionTitle,
                        { color: colors.muted, fontSize: getFontSize(12, largeText) },
                      ]}
                    >
                      Recent Chats
                    </Text>

                    {recentChats.length === 0 ? (
                      <Text
                        style={[
                          styles.menuEmptyText,
                          { color: colors.muted, fontSize: getFontSize(13, largeText) },
                        ]}
                      >
                        No recent chats
                      </Text>
                    ) : (
                      recentChats.map((chat, index) => (
                        <Pressable
                          key={`${chat}-${index}`}
                          style={styles.menuItem}
                          onPress={() => {
                            setInput(chat);
                            setMenuOpen(false);
                          }}
                        >
                          <Text
                            style={[
                              styles.menuText,
                              { color: colors.text, fontSize: getFontSize(13, largeText) },
                            ]}
                            numberOfLines={1}
                          >
                            {chat}
                          </Text>
                        </Pressable>
                      ))
                    )}
                  </View>
                ) : null}
              </View>
            </View>

            <View
              style={[
                styles.welcomeBox,
                {
                  backgroundColor: colors.card,
                  borderColor: colors.border,
                },
              ]}
            >
              <Text
                style={[
                  styles.welcomeText,
                  {
                    color: colors.text,
                    fontSize: getFontSize(15, largeText),
                  },
                ]}
              >
                Hi, I’m Campus AI. Ask me about rooms, campus information, or
                uploaded PDF documents.
              </Text>
            </View>

            <FlatList
              ref={listRef}
              data={messages}
              keyExtractor={(item) => item.id}
              renderItem={({ item }) => <ChatBubble role={item.role} text={item.text} />}
              contentContainerStyle={styles.chatList}
              showsVerticalScrollIndicator={false}
            />

            {typing ? (
              <View style={styles.typingRow}>
                <ActivityIndicator color={colors.primary} />
                <Text
                  style={[
                    styles.typingText,
                    { color: colors.muted, fontSize: getFontSize(13, largeText) },
                  ]}
                >
                  Campus AI is typing...
                </Text>
              </View>
            ) : null}

            {attachedFileName ? (
              <View
                style={[
                  styles.attachmentChip,
                  {
                    backgroundColor: colors.primarySoft,
                    borderColor: colors.border,
                  },
                ]}
              >
                <Text
                  style={[
                    styles.attachmentText,
                    {
                      color: colors.text,
                      fontSize: getFontSize(13, largeText),
                    },
                  ]}
                  numberOfLines={1}
                >
                  {attachedFileName}
                </Text>

                <Pressable onPress={() => setAttachedFileName(null)}>
                  <X color={colors.text} size={16} />
                </Pressable>
              </View>
            ) : null}

            

            <View
              style={[
                styles.inputContainer,
                {
                  backgroundColor: colors.surface,
                  borderColor: colors.border,
                },
              ]}
            >
              <Pressable
                onPress={handlePickDocument}
                style={[
                  styles.iconButton,
                  {
                    backgroundColor: colors.surface2,
                    borderColor: colors.border,
                  },
                ]}
              >
                <Plus color={colors.text} size={18} />
              </Pressable>

              <TextInput
                value={input}
                onChangeText={setInput}
                placeholder="Ask a question..."
                placeholderTextColor={colors.muted}
                style={[
                  styles.input,
                  {
                    color: colors.text,
                    fontSize: getFontSize(15, largeText),
                  },
                ]}
                multiline
              />

              <Pressable
                onPress={() => handleSend()}
                disabled={!canSend}
                style={[
                  styles.sendButton,
                  {
                    backgroundColor: colors.primary,
                    opacity: canSend ? 1 : 0.7,
                  },
                ]}
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
  safe: {
    flex: 1,
  },
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
  headerTitle: {
    fontWeight: "900",
  },
  menuWrapper: {
    position: "relative",
    zIndex: 30,
  },
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
  menuItem: {
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  menuText: {
    fontWeight: "500",
  },
  menuDivider: {
    height: 1,
    marginVertical: 6,
    marginHorizontal: 12,
  },
  menuSectionTitle: {
    fontWeight: "700",
    paddingHorizontal: 14,
    paddingTop: 4,
    paddingBottom: 6,
    textTransform: "uppercase",
  },
  menuEmptyText: {
    paddingHorizontal: 14,
    paddingBottom: 8,
  },
  welcomeBox: {
    borderRadius: 20,
    borderWidth: 1,
    padding: 16,
    marginBottom: 12,
  },
  welcomeText: {
    fontWeight: "500",
    lineHeight: 22,
  },
  promptsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginBottom: 8,
  },
  chatList: {
    paddingTop: 8,
    paddingBottom: 12,
    flexGrow: 1,
  },
  typingRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
    gap: 8,
  },
  typingText: {
    fontWeight: "500",
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
  attachmentText: {
    flex: 1,
    fontWeight: "600",
  },
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