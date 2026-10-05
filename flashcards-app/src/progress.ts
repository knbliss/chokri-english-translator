import AsyncStorage from "@react-native-async-storage/async-storage";

const STORAGE_KEY = "chokri-flashcards:known-ids:v1";

export async function loadKnownIds(): Promise<Set<string>> {
  try {
    const raw = await AsyncStorage.getItem(STORAGE_KEY);
    if (!raw) return new Set();
    const arr: string[] = JSON.parse(raw);
    return new Set(arr);
  } catch {
    return new Set();
  }
}

export async function saveKnownIds(ids: Set<string>): Promise<void> {
  try {
    await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(ids)));
  } catch {
    // best-effort persistence; ignore failures
  }
}
