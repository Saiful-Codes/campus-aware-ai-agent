import React, { useEffect, useRef, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { getFontSize, palette } from "../constants/theme";
import { useAppSettings } from "../context/AppSettingsContext";

type Props = {
  role: "user" | "assistant";
  text: string;
  streaming?: boolean;
  onStreamComplete?: () => void;
};

const WORD_INTERVAL_MS = 40; // speed between words

export default function ChatBubble({ role, text, streaming = false, onStreamComplete }: Props) {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];
  const isUser = role === "user";

  const [displayedText, setDisplayedText] = useState(streaming ? "" : text);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const wordIndexRef = useRef(0);

  useEffect(() => {
    // If not streaming, just show the full text immediately
    if (!streaming) {
      setDisplayedText(text);
      return;
    }

    // Reset when text changes (new streaming message starts)
    setDisplayedText("");
    wordIndexRef.current = 0;

    const words = text.split(" ");

    intervalRef.current = setInterval(() => {
      wordIndexRef.current += 1;
      const slice = words.slice(0, wordIndexRef.current).join(" ");
      setDisplayedText(slice);

      if (wordIndexRef.current >= words.length) {
        clearInterval(intervalRef.current!);
        intervalRef.current = null;
        onStreamComplete?.();
      }
    }, WORD_INTERVAL_MS);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [text, streaming]);

  const showCursor = streaming && displayedText !== text;

  return (
    <View style={[styles.row, isUser ? styles.userRow : styles.assistantRow]}>
      {!isUser && (
        <View style={[styles.avatar, { backgroundColor: colors.primary }]}>
          <Text style={styles.avatarText}>AI</Text>
        </View>
      )}
      <View
        style={[
          styles.bubble,
          {
            backgroundColor: isUser ? colors.bubbleUser : colors.bubbleAssistant,
            borderColor: colors.border,
          },
        ]}
      >
        <Text
          style={[
            styles.text,
            {
              color: isUser ? colors.white : colors.text,
              fontSize: getFontSize(14, largeText),
              lineHeight: getFontSize(22, largeText),
            },
          ]}
        >
          {displayedText}
          {showCursor && (
            <Text style={{ color: colors.primary, fontWeight: "900" }}>▍</Text>
          )}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    width: "100%",
    marginBottom: 14,
    flexDirection: "row",
    alignItems: "flex-end",
    gap: 8,
  },
  userRow: {
    justifyContent: "flex-end",
  },
  assistantRow: {
    justifyContent: "flex-start",
  },
  avatar: {
    width: 28,
    height: 28,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 2,
  },
  avatarText: {
    color: "#fff",
    fontSize: 9,
    fontWeight: "900",
    letterSpacing: 0.5,
  },
  bubble: {
    maxWidth: "82%",
    paddingHorizontal: 14,
    paddingVertical: 12,
    borderRadius: 18,
    borderWidth: 1,
  },
  text: {
    fontWeight: "500",
  },
});
