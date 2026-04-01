import React from "react";
import { Pressable, StyleSheet, Text } from "react-native";
import { getFontSize, palette } from "../constants/theme";
import { useAppSettings } from "../context/AppSettingsContext";

type Props = {
  label: string;
  onPress: () => void;
};

export default function QuickPrompt({ label, onPress }: Props) {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];

  return (
    <Pressable
      onPress={onPress}
      style={[
        styles.prompt,
        {
          backgroundColor: colors.surface,
          borderColor: colors.border,
        },
      ]}
    >
      <Text
        style={[
          styles.promptText,
          {
            color: colors.text,
            fontSize: getFontSize(13, largeText),
          },
        ]}
      >
        {label}
      </Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  prompt: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 999,
    borderWidth: 1,
    marginRight: 10,
    marginBottom: 10,
  },
  promptText: {
    fontWeight: "600",
  },
});