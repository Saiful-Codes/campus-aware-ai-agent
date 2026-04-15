import React, { useEffect, useRef, useState } from "react";
import { Animated, StyleSheet, Text, View } from "react-native";
import { getFontSize, palette } from "../constants/theme";
import { useAppSettings } from "../context/AppSettingsContext";

type Props = {
  role: "user" | "assistant";
  text: string;
  streaming?: boolean;
  onStreamComplete?: () => void;
};

const WORD_INTERVAL_MS = 40;
const DOT_UP_MS = 220;
const DOT_DOWN_MS = 220;
const DOT_IDLE_MS = 900; // total loop = DOT_UP + DOT_DOWN + DOT_IDLE = 1340ms

export default function ChatBubble({ role, text, streaming = false, onStreamComplete }: Props) {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];
  const isUser = role === "user";

  // "thinking" = waiting for API response (placeholder text)
  const isThinking = streaming && text === "…";

  const [displayedText, setDisplayedText] = useState(streaming ? "" : text);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const wordIndexRef = useRef(0);

  // ── Bouncing dot animated values ──────────────────────────────────────────
  const dot1 = useRef(new Animated.Value(0)).current;
  const dot2 = useRef(new Animated.Value(0)).current;
  const dot3 = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (!isThinking) {
      [dot1, dot2, dot3].forEach((d) => d.setValue(0));
      return;
    }

    const makeDotAnim = (val: Animated.Value, delay: number) =>
      Animated.loop(
        Animated.sequence([
          Animated.delay(delay),
          Animated.timing(val, { toValue: -7, duration: DOT_UP_MS, useNativeDriver: true }),
          Animated.timing(val, { toValue: 0, duration: DOT_DOWN_MS, useNativeDriver: true }),
          Animated.delay(DOT_IDLE_MS - delay),
        ])
      );

    const anims = [
      makeDotAnim(dot1, 0),
      makeDotAnim(dot2, 180),
      makeDotAnim(dot3, 360),
    ];
    anims.forEach((a) => a.start());

    return () => {
      anims.forEach((a) => a.stop());
      [dot1, dot2, dot3].forEach((d) => d.setValue(0));
    };
  }, [isThinking]);

  // ── Word-by-word streaming ─────────────────────────────────────────────────
  useEffect(() => {
    // Skip word animation while thinking or not streaming
    if (!streaming || text === "…") return;

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

  // Show cursor while words are still appearing
  const showCursor = streaming && !isThinking && displayedText !== text;

  // ── Thinking state: animated dots ─────────────────────────────────────────
  if (isThinking) {
    return (
      <View style={[styles.row, styles.assistantRow]}>
        <View style={[styles.avatar, { backgroundColor: colors.primary }]}>
          <Text style={styles.avatarText}>AI</Text>
        </View>
        <View
          style={[
            styles.bubble,
            { backgroundColor: colors.bubbleAssistant, borderColor: colors.border },
          ]}
        >
          <View style={styles.dotsContainer}>
            {[dot1, dot2, dot3].map((dot, i) => (
              <Animated.View
                key={i}
                style={[
                  styles.dot,
                  { backgroundColor: colors.primary },
                  { transform: [{ translateY: dot }] },
                ]}
              />
            ))}
          </View>
        </View>
      </View>
    );
  }

  // ── Normal bubble ─────────────────────────────────────────────────────────
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
  userRow: { justifyContent: "flex-end" },
  assistantRow: { justifyContent: "flex-start" },
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
  text: { fontWeight: "500" },
  dotsContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingVertical: 4,
    paddingHorizontal: 2,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
});
