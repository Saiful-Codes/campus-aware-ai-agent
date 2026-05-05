import React from "react";
import { Platform, StyleSheet, Text, View } from "react-native";
import { getFontSize, palette } from "../constants/theme";
import { useAppSettings } from "../context/AppSettingsContext";

type Props = {
  text: string;
  color: string;
};

// Parse inline bold/italic/code within a string
function InlineText({ raw, baseStyle }: { raw: string; baseStyle: object }) {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];

  // Split on **bold**, *italic*, `code`
  const parts: { text: string; bold?: boolean; italic?: boolean; code?: boolean }[] = [];
  const regex = /(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)/g;
  let last = 0;
  let match;

  while ((match = regex.exec(raw)) !== null) {
    if (match.index > last) {
      parts.push({ text: raw.slice(last, match.index) });
    }
    if (match[0].startsWith("**")) {
      parts.push({ text: match[2], bold: true });
    } else if (match[0].startsWith("`")) {
      parts.push({ text: match[4], code: true });
    } else {
      parts.push({ text: match[3], italic: true });
    }
    last = match.index + match[0].length;
  }
  if (last < raw.length) parts.push({ text: raw.slice(last) });

  return (
    <Text style={baseStyle}>
      {parts.map((p, i) => {
        if (p.code) {
          return (
            <Text
              key={i}
              style={[
                baseStyle,
                styles.inlineCode,
                {
                  backgroundColor: colors.surface2,
                  color: colors.primary,
                  fontSize: getFontSize(13, largeText),
                },
              ]}
            >
              {p.text}
            </Text>
          );
        }
        return (
          <Text
            key={i}
            style={[
              baseStyle,
              p.bold && styles.bold,
              p.italic && styles.italic,
            ]}
          >
            {p.text}
          </Text>
        );
      })}
    </Text>
  );
}

export default function MarkdownRenderer({ text, color }: Props) {
  const { themeMode, largeText } = useAppSettings();
  const colors = palette[themeMode];

  const baseTextStyle = {
    color,
    fontSize: getFontSize(14, largeText),
    lineHeight: getFontSize(22, largeText),
    fontWeight: "500" as const,
  };

  const lines = text.split("\n");
  const blocks: React.ReactNode[] = [];
  let i = 0;
  let listItems: string[] = [];
  let orderedItems: string[] = [];
  let blockKey = 0;

  const flushList = () => {
    if (listItems.length > 0) {
      blocks.push(
        <View key={`ul-${blockKey++}`} style={styles.list}>
          {listItems.map((item, idx) => (
            <View key={idx} style={styles.listRow}>
              <Text style={[baseTextStyle, styles.bullet]}>•</Text>
              <View style={styles.listContent}>
                <InlineText raw={item} baseStyle={baseTextStyle} />
              </View>
            </View>
          ))}
        </View>
      );
      listItems = [];
    }
  };

  const flushOrdered = () => {
    if (orderedItems.length > 0) {
      blocks.push(
        <View key={`ol-${blockKey++}`} style={styles.list}>
          {orderedItems.map((item, idx) => (
            <View key={idx} style={styles.listRow}>
              <Text style={[baseTextStyle, styles.bullet, { minWidth: 22 }]}>
                {idx + 1}.
              </Text>
              <View style={styles.listContent}>
                <InlineText raw={item} baseStyle={baseTextStyle} />
              </View>
            </View>
          ))}
        </View>
      );
      orderedItems = [];
    }
  };

  while (i < lines.length) {
    const line = lines[i];

    // Heading 1
    if (/^# (.+)/.test(line)) {
      flushList(); flushOrdered();
      const content = line.replace(/^# /, "");
      blocks.push(
        <Text
          key={`h1-${blockKey++}`}
          style={[baseTextStyle, styles.h1, { color, fontSize: getFontSize(20, largeText) }]}
        >
          {content}
        </Text>
      );
      i++; continue;
    }

    // Heading 2
    if (/^## (.+)/.test(line)) {
      flushList(); flushOrdered();
      const content = line.replace(/^## /, "");
      blocks.push(
        <Text
          key={`h2-${blockKey++}`}
          style={[baseTextStyle, styles.h2, { color, fontSize: getFontSize(17, largeText) }]}
        >
          {content}
        </Text>
      );
      i++; continue;
    }

    // Heading 3
    if (/^### (.+)/.test(line)) {
      flushList(); flushOrdered();
      const content = line.replace(/^### /, "");
      blocks.push(
        <Text
          key={`h3-${blockKey++}`}
          style={[baseTextStyle, styles.h3, { color, fontSize: getFontSize(15, largeText) }]}
        >
          {content}
        </Text>
      );
      i++; continue;
    }

    // Unordered list
    if (/^[-*] (.+)/.test(line)) {
      flushOrdered();
      listItems.push(line.replace(/^[-*] /, ""));
      i++; continue;
    }

    // Ordered list
    if (/^\d+\. (.+)/.test(line)) {
      flushList();
      orderedItems.push(line.replace(/^\d+\. /, ""));
      i++; continue;
    }

    // Blockquote
    if (/^> (.+)/.test(line)) {
      flushList(); flushOrdered();
      const content = line.replace(/^> /, "");
      blocks.push(
        <View
          key={`bq-${blockKey++}`}
          style={[styles.blockquote, { borderLeftColor: colors.primary }]}
        >
          <InlineText
            raw={content}
            baseStyle={[baseTextStyle, { color: colors.muted }] as any}
          />
        </View>
      );
      i++; continue;
    }

    // Empty line — flush lists, add spacing
    if (line.trim() === "") {
      flushList(); flushOrdered();
      blocks.push(<View key={`sp-${blockKey++}`} style={styles.spacer} />);
      i++; continue;
    }

    // Horizontal rule
    if (/^---+$/.test(line.trim())) {
      flushList(); flushOrdered();
      blocks.push(
        <View
          key={`hr-${blockKey++}`}
          style={[styles.hr, { backgroundColor: colors.border }]}
        />
      );
      i++; continue;
    }

    // Paragraph
    flushList(); flushOrdered();
    blocks.push(
      <InlineText key={`p-${blockKey++}`} raw={line} baseStyle={baseTextStyle} />
    );
    i++;
  }

  flushList();
  flushOrdered();

  return <View style={styles.container}>{blocks}</View>;
}

const styles = StyleSheet.create({
  container: { gap: 2 },
  bold: { fontWeight: "700" },
  italic: { fontStyle: "italic" },
  inlineCode: {
    fontFamily: Platform.OS === "ios" ? "Courier New" : "monospace",
    borderRadius: 4,
    paddingHorizontal: 4,
  },
  h1: { fontWeight: "900", marginBottom: 2, marginTop: 4 },
  h2: { fontWeight: "800", marginBottom: 2, marginTop: 4 },
  h3: { fontWeight: "700", marginBottom: 1, marginTop: 3 },
  list: { gap: 4, marginVertical: 2 },
  listRow: { flexDirection: "row", alignItems: "flex-start", gap: 6 },
  bullet: { fontWeight: "700", lineHeight: 22, width: 14 },
  listContent: { flex: 1 },
  blockquote: {
    borderLeftWidth: 3,
    paddingLeft: 10,
    marginVertical: 4,
    opacity: 0.85,
  },
  spacer: { height: 6 },
  hr: { height: 1, marginVertical: 8, opacity: 0.4 },
});

