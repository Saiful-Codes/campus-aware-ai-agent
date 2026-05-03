import React, { useEffect, useRef, useState } from "react";
import { Animated, StyleSheet, Text, View } from "react-native";
import { getFontSize, palette } from "../constants/theme";
import { useAppSettings } from "../context/AppSettingsContext";
import MarkdownRenderer from "./MarkdownRenderer";

type Props = {
  role: "user" | "assistant";
  text: string;
  streaming?: boolean;
  onStreamComplete?: () => void;
};

const CHAR_INTERVAL_MS = 8;

// ── Claude-style spinner ──────────────────────────────────────────────────────
// Anthropic logo = 4 bars at 0/45/90/135° → 8-pointed starburst.
// A clockwise opacity sweep fires through each bar one at a time:
// bar brightens → next bar brightens → previous dims → loops.
// This is the exact visual Claude uses for its thinking state.
function ClaudeSpinner({ color }: { color: string }) {
  // Start: bar 0 fully bright, others dim
  const opacities = useRef(
    [0, 1, 2, 3].map((i) => new Animated.Value(i === 0 ? 1 : 0.22))
  ).current;

  useEffect(() => {
    const STEP_MS = 160; // ms each step — matches Claude's cadence
    const n = opacities.length;

    const sweep = Animated.loop(
      Animated.sequence(
        [0, 1, 2, 3].map((i) =>
          Animated.parallel([
            // Current bar fades out
            Animated.timing(opacities[i], {
              toValue: 0.22,
              duration: STEP_MS,
              useNativeDriver: true,
            }),
            // Next bar lights up
            Animated.timing(opacities[(i + 1) % n], {
              toValue: 1,
              duration: STEP_MS,
              useNativeDriver: true,
            }),
          ])
        )
      )
    );

    sweep.start();
    return () => {
      sweep.stop();
      opacities.forEach((o, i) => o.setValue(i === 0 ? 1 : 0.22));
    };
  }, []);

  return (
    <View style={spinner.container}>
      {[0, 45, 90, 135].map((deg, i) => (
        <Animated.View
          key={i}
          style={[
            spinner.bar,
            {
              backgroundColor: color,
              opacity: opacities[i],
              transform: [{ rotate: `${deg}deg` }],
            },
          ]}
        />
      ))}
    </View>
  );
}

// ── Main component ────────────────────────────────────────────────────────────
export default function ChatBubble({
  role,
  text,
  streaming = false,
  onStreamComplete,
}: Props) {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];
  const isUser = role === "user";

  const isThinking = streaming && text === "…";

  const [displayedText, setDisplayedText] = useState(streaming ? "" : text);
  const intervalRef  = useRef<ReturnType<typeof setInterval> | null>(null);
  const charIndexRef = useRef(0);

  // Character-by-character streaming
  useEffect(() => {
    if (!streaming || text === "…") return;
    setDisplayedText("");
    charIndexRef.current = 0;
    intervalRef.current = setInterval(() => {
      charIndexRef.current += 3;
      setDisplayedText(text.slice(0, charIndexRef.current));
      if (charIndexRef.current >= text.length) {
        setDisplayedText(text);
        clearInterval(intervalRef.current!);
        intervalRef.current = null;
        onStreamComplete?.();
      }
    }, CHAR_INTERVAL_MS);
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [text, streaming]);

  // ── Thinking state — compact pill, no avatar, just the Claude spinner ──────
  if (isThinking) {
    return (
      <View style={[styles.row, styles.assistantRow]}>
        <View
          style={[
            styles.thinkingPill,
            {
              backgroundColor: colors.bubbleAssistant,
              borderColor:     colors.border,
            },
          ]}
        >
          <ClaudeSpinner color={colors.primary} />
        </View>
      </View>
    );
  }

  // ── Normal bubble ──────────────────────────────────────────────────────────
  const textToShow = streaming ? displayedText : text;

  return (
    <View style={[styles.row, isUser ? styles.userRow : styles.assistantRow]}>
      <View
        style={[
          styles.bubble,
          {
            backgroundColor: isUser ? colors.bubbleUser : colors.bubbleAssistant,
            borderColor: colors.border,
          },
        ]}
      >
        {isUser ? (
          <Text
            style={[
              styles.text,
              {
                color:      colors.white,
                fontSize:   getFontSize(14, largeText),
                lineHeight: getFontSize(22, largeText),
              },
            ]}
          >
            {textToShow}
          </Text>
        ) : (
          <MarkdownRenderer text={textToShow} color={colors.text} />
        )}
      </View>
    </View>
  );
}

// ── Spinner styles ────────────────────────────────────────────────────────────
const spinner = StyleSheet.create({
  container: {
    width: 26,
    height: 26,
    alignItems: "center",
    justifyContent: "center",
  },
  // Each bar covers one axis of the starburst; 4 bars × 2 ends = 8 points
  bar: {
    position: "absolute",
    width: 3,
    height: 26,
    borderRadius: 2,
  },
});

// ── Bubble styles ─────────────────────────────────────────────────────────────
const styles = StyleSheet.create({
  row: {
    width: "100%",
    marginBottom: 14,
    flexDirection: "row",
    alignItems: "flex-end",
    gap: 8,
  },
  userRow:      { justifyContent: "flex-end" },
  assistantRow: { justifyContent: "flex-start" },

  thinkingPill: {
    width: 52,
    height: 44,
    borderRadius: 22,
    borderWidth: 1,
    alignItems: "center",
    justifyContent: "center",
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
  text: { fontWeight: "500" },
});
