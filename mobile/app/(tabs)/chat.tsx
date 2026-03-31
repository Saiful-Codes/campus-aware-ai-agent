import * as DocumentPicker from "expo-document-picker";
import { router } from "expo-router";
import { Plus, Send, Settings, X } from "lucide-react-native";
import React, { useMemo, useRef, useState } from "react";
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
  View,
} from "react-native";
import ChatBubble from "../../src/components/ChatBubble";
import QuickPrompt from "../../src/components/QuickPrompt";
import { getFontSize, palette } from "../../src/constants/theme";
import { useAppSettings } from "../../src/context/AppSettingsContext";

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
};

const quickPrompts = [
  "Does PW-202 get stuffy in the afternoon?",
  "Tell me about La Trobe study spaces",
  "Summarise this uploaded PDF",
  "Where can I find campus maps?",
];

export default function ChatScreen() {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      text: "Hi, I’m Campus AI. Ask me about rooms, campus information, or uploaded PDF documents.",
    },
  ]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [attachedFileName, setAttachedFileName] = useState<string | null>(null);

  const listRef = useRef<FlatList<Message>>(null);

  const canSend = useMemo(() => input.trim().length > 0 || !!attachedFileName, [input, attachedFileName]);

  const scrollToBottom = () => {
    setTimeout(() => {
      listRef.current?.scrollToEnd({ animated: true });
    }, 100);
  };

  const fakeAssistantReply = (query: string, fileName?: string | null) => {
    if (fileName && !query.trim()) {
      return `The document "${fileName}" is attached. Once backend document processing is connected, I’ll answer PDF questions here.`;
    }

    return `You asked: "${query}". This chat UI is ready to connect to the Campus AI backend for campus, room, and document-based responses.`;
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

  const handleSend = async (promptText?: string) => {
    const textToSend = promptText ?? input.trim();

    if (!textToSend && !attachedFileName) return;

    const userMessage: Message = {
      id: `${Date.now()}-user`,
      role: "user",
      text: textToSend || `Uploaded document: ${attachedFileName}`,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setTyping(true);
    scrollToBottom();

    setTimeout(() => {
      const assistantMessage: Message = {
        id: `${Date.now()}-assistant`,
        role: "assistant",
        text: fakeAssistantReply(textToSend, attachedFileName),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setTyping(false);
      setAttachedFileName(null);
      scrollToBottom();
    }, 900);
  };

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.background }]}>
      <KeyboardAvoidingView
        style={styles.safe}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <View style={styles.container}>
          <View style={styles.header}>
            <View>
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
              
            </View>

            <Pressable
              onPress={() => router.push("/settings")}
              style={[
                styles.settingsButton,
                {
                  backgroundColor: colors.surface,
                  borderColor: colors.border,
                },
              ]}
            >
              <Settings color={colors.text} size={18} />
            </Pressable>
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

          <View style={styles.promptsRow}>
            {quickPrompts.map((prompt) => (
              <QuickPrompt key={prompt} label={prompt} onPress={() => handleSend(prompt)} />
            ))}
          </View>

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
  },
  headerTitle: {
    fontWeight: "900",
  },
  headerSubtitle: {
    marginTop: 4,
    fontWeight: "500",
  },
  settingsButton: {
    width: 42,
    height: 42,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
  },
  promptsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginBottom: 8,
  },
  chatList: {
    paddingTop: 8,
    paddingBottom: 12,
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