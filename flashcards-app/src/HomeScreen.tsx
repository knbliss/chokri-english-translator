import React from "react";
import { Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";
import type { TypeSummary } from "./types";

type Props = {
  types: TypeSummary[];
  totalCount: number;
  knownCount: number;
  onSelectType: (type: string) => void;
};

const COLORS: Record<string, string> = {
  sentence: "#2f6fed",
  word: "#1f8a4c",
};

export default function HomeScreen({
  types,
  totalCount,
  knownCount,
  onSelectType,
}: Props) {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>Chokri Flashcards</Text>
      <Text style={styles.subtitle}>
        {totalCount} cards · {knownCount} marked known
      </Text>

      <View style={styles.spacer} />

      <Text style={styles.prompt}>What would you like to study?</Text>

      {types.map((t) => (
        <Pressable
          key={t.id}
          style={[styles.card, { backgroundColor: COLORS[t.id] ?? "#2f6fed" }]}
          onPress={() => onSelectType(t.id)}
        >
          <Text style={styles.cardTitle}>{t.name}</Text>
          <Text style={styles.cardDesc}>{t.description}</Text>
          <Text style={styles.cardCount}>{t.count} cards</Text>
        </Pressable>
      ))}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f1117", paddingHorizontal: 20 },
  title: { fontSize: 28, fontWeight: "700", color: "#fff", marginTop: 12 },
  subtitle: { fontSize: 14, color: "#9aa0ac", marginTop: 4 },
  spacer: { height: 20 },
  prompt: { color: "#9aa0ac", fontSize: 14, marginBottom: 12 },
  card: {
    borderRadius: 16,
    padding: 22,
    marginBottom: 16,
  },
  cardTitle: { color: "#fff", fontSize: 22, fontWeight: "700" },
  cardDesc: { color: "#e3e9ff", fontSize: 14, marginTop: 6, lineHeight: 20 },
  cardCount: { color: "#c0d3ff", fontSize: 13, marginTop: 14 },
});
