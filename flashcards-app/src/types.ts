export type CardType = "word" | "sentence";

export type Card = {
  id: string;
  type: CardType;
  chokri: string;
  english: string;
};

export type TypeSummary = {
  id: CardType;
  name: string;
  description: string;
  count: number;
};

export type Deck = {
  generatedFrom: string;
  count: number;
  types: TypeSummary[];
  cards: Card[];
};

export type Direction = "chokri-to-english" | "english-to-chokri";
