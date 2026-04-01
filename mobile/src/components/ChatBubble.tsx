import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { getFontSize, palette } from "../constants/theme";
import { useAppSettings } from "../context/AppSettingsContext";

type Props = {
  role: "user" | "assistant";
  text: string;
};

export default function ChatBubble({ role, text }: Props) {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];
  const isUser = role === "user";

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
        <Text
          style={[
            styles.text,
            {
              color: isUser ? colors.white : colors.text,
              fontSize: getFontSize(14, largeText),
              lineHeight: getFontSize(20, largeText),
            },
          ]}
        >
          {text}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    width: "100%",
    marginBottom: 12,
    flexDirection: "row",
  },
  userRow: {
    justifyContent: "flex-end",
  },
  assistantRow: {
    justifyContent: "flex-start",
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