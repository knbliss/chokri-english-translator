import React, { useEffect, useMemo, useState } from "react";
import { StatusBar } from "expo-status-bar";

import deckData from "./assets/data/deck.json";
import HomeScreen from "./src/HomeScreen";
import FlashcardScreen from "./src/FlashcardScreen";
import { loadKnownIds, saveKnownIds } from "./src/progress";
import type { Card, Deck, Direction } from "./src/types";

const deck = deckData as Deck;

function shuffle<T>(arr: T[]): T[] {
  const copy = arr.slice();
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

export default function App() {
  const [selectedType, setSelectedType] = useState<string | undefined>(
    undefined
  );
  const [direction, setDirection] = useState<Direction>("chokri-to-english");
  const [knownIds, setKnownIds] = useState<Set<string>>(new Set());
  const [orderedCards, setOrderedCards] = useState<Card[]>([]);

  useEffect(() => {
    loadKnownIds().then(setKnownIds);
  }, []);

  function baseCardsFor(type: string): Card[] {
    return deck.cards.filter((c) => c.type === type);
  }

  function openType(type: string) {
    setSelectedType(type);
    setOrderedCards(baseCardsFor(type));
  }

  function reshuffle() {
    setOrderedCards((prev) => shuffle(prev));
  }

  function toggleKnown(id: string) {
    setKnownIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      saveKnownIds(next);
      return next;
    });
  }

  const title = useMemo(() => {
    const t = deck.types.find((x) => x.id === selectedType);
    return t?.name ?? "";
  }, [selectedType]);

  if (selectedType === undefined) {
    return (
      <>
        <HomeScreen
          types={deck.types}
          totalCount={deck.count}
          knownCount={knownIds.size}
          onSelectType={openType}
        />
        <StatusBar style="light" />
      </>
    );
  }

  return (
    <>
      <FlashcardScreen
        title={title}
        cards={orderedCards}
        direction={direction}
        knownIds={knownIds}
        onToggleDirection={() =>
          setDirection((d) =>
            d === "chokri-to-english" ? "english-to-chokri" : "chokri-to-english"
          )
        }
        onToggleKnown={toggleKnown}
        onShuffle={reshuffle}
        onBack={() => setSelectedType(undefined)}
      />
      <StatusBar style="light" />
    </>
  );
}
