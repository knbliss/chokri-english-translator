import React, { useMemo, useRef, useState } from "react";
import {
  Animated,
  PanResponder,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import type { Card, Direction } from "./types";

type Props = {
  title: string;
  cards: Card[];
  direction: Direction;
  knownIds: Set<string>;
  onToggleDirection: () => void;
  onToggleKnown: (id: string) => void;
  onShuffle: () => void;
  onBack: () => void;
};

const SWIPE_THRESHOLD = 100;

export default function FlashcardScreen({
  title,
  cards,
  direction,
  knownIds,
  onToggleDirection,
  onToggleKnown,
  onShuffle,
  onBack,
}: Props) {
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const pan = useRef(new Animated.ValueXY()).current;

  const card = cards[index];
  const isKnown = card ? knownIds.has(card.id) : false;

  const front = direction === "chokri-to-english" ? card?.chokri : card?.english;
  const back = direction === "chokri-to-english" ? card?.english : card?.chokri;

  function goTo(next: number) {
    if (cards.length === 0) return;
    const clamped = ((next % cards.length) + cards.length) % cards.length;
    setIndex(clamped);
    setFlipped(false);
    pan.setValue({ x: 0, y: 0 });
  }

  const panResponder = useMemo(
    () =>
      PanResponder.create({
        onMoveShouldSetPanResponder: (_, gesture) =>
          Math.abs(gesture.dx) > 8,
        onPanResponderMove: Animated.event(
          [null, { dx: pan.x, dy: pan.y }],
          { useNativeDriver: false }
        ),
        onPanResponderRelease: (_, gesture) => {
          if (gesture.dx > SWIPE_THRESHOLD) {
            goTo(index - 1);
          } else if (gesture.dx < -SWIPE_THRESHOLD) {
            goTo(index + 1);
          } else {
            Animated.spring(pan, {
              toValue: { x: 0, y: 0 },
              useNativeDriver: false,
            }).start();
          }
        },
      }),
    [index, cards.length]
  );

  if (!card) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.empty}>No cards in this set.</Text>
        <Pressable style={styles.backButton} onPress={onBack}>
          <Text style={styles.backButtonText}>Back</Text>
        </Pressable>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Pressable onPress={onBack}>
          <Text style={styles.headerLink}>‹ Home</Text>
        </Pressable>
        <Text style={styles.headerTitle}>{title}</Text>
        <Pressable onPress={onShuffle}>
          <Text style={styles.headerLink}>Shuffle</Text>
        </Pressable>
      </View>

      <Text style={styles.progress}>
        {index + 1} / {cards.length}
      </Text>

      <Animated.View
        {...panResponder.panHandlers}
        style={[styles.card, { transform: pan.getTranslateTransform() }]}
      >
        <Pressable
          style={styles.cardPressable}
          onPress={() => setFlipped((f) => !f)}
        >
          <Text style={styles.cardText}>{flipped ? back : front}</Text>
          <Text style={styles.hint}>
            {flipped ? "tap to show prompt" : "tap to reveal translation"}
          </Text>
        </Pressable>
      </Animated.View>

      <View style={styles.controls}>
        <Pressable style={styles.navButton} onPress={() => goTo(index - 1)}>
          <Text style={styles.navButtonText}>‹ Prev</Text>
        </Pressable>
        <Pressable
          style={[styles.knownButton, isKnown && styles.knownButtonActive]}
          onPress={() => onToggleKnown(card.id)}
        >
          <Text
            style={[
              styles.knownButtonText,
              isKnown && styles.knownButtonTextActive,
            ]}
          >
            {isKnown ? "✓ Known" : "Mark known"}
          </Text>
        </Pressable>
        <Pressable style={styles.navButton} onPress={() => goTo(index + 1)}>
          <Text style={styles.navButtonText}>Next ›</Text>
        </Pressable>
      </View>

      <Pressable style={styles.directionToggle} onPress={onToggleDirection}>
        <Text style={styles.directionToggleText}>
          {direction === "chokri-to-english"
            ? "Chokri → English (tap to flip direction)"
            : "English → Chokri (tap to flip direction)"}
        </Text>
      </Pressable>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f1117", paddingHorizontal: 20 },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 8,
  },
  headerLink: { color: "#2f6fed", fontSize: 15, fontWeight: "600" },
  headerTitle: { color: "#fff", fontSize: 16, fontWeight: "700" },
  progress: { color: "#7d8591", textAlign: "center", marginTop: 10 },
  card: {
    flex: 1,
    marginTop: 16,
    marginBottom: 16,
    backgroundColor: "#1a1d27",
    borderRadius: 18,
  },
  cardPressable: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 24,
  },
  cardText: {
    color: "#fff",
    fontSize: 24,
    textAlign: "center",
    lineHeight: 32,
  },
  hint: {
    position: "absolute",
    bottom: 16,
    color: "#5b6270",
    fontSize: 12,
  },
  controls: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  navButton: { padding: 12 },
  navButtonText: { color: "#2f6fed", fontSize: 16, fontWeight: "600" },
  knownButton: {
    paddingVertical: 10,
    paddingHorizontal: 18,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#2f6fed",
  },
  knownButtonActive: { backgroundColor: "#1f8a4c", borderColor: "#1f8a4c" },
  knownButtonText: { color: "#2f6fed", fontWeight: "600" },
  knownButtonTextActive: { color: "#fff" },
  directionToggle: { paddingVertical: 16, alignItems: "center" },
  directionToggleText: { color: "#7d8591", fontSize: 13 },
  empty: { color: "#fff", textAlign: "center", marginTop: 40 },
  backButton: { alignSelf: "center", marginTop: 16 },
  backButtonText: { color: "#2f6fed", fontSize: 16 },
});
