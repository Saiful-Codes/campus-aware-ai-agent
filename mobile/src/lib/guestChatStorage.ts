import AsyncStorage from "@react-native-async-storage/async-storage";

// Guest chat history is session-ephemeral: it lives only in React state for the
// lifetime of a guest session and is never persisted per-user. These keys are
// LEGACY — older builds wrote guest threads/messages here using device-global
// keys, which let one guest inherit a previous guest's conversations (privacy
// leak). We keep the key list so we can proactively purge any stale data left
// on a device/browser at every guest-session boundary (entering guest mode and
// logging out).
export const GUEST_CHAT_STORAGE_KEYS = [
  "campus_ai_threads_v2",
  "campus_ai_threads_v2_messages",
  "campus_ai_active_thread",
];

/**
 * Remove any persisted guest chat data from local storage.
 *
 * Called when a guest session begins and when a user logs out so that a fresh
 * guest can never see another session's conversations. Safe to call when no
 * data exists; failures are swallowed because this is best-effort hygiene.
 */
export async function clearGuestChatStorage(): Promise<void> {
  try {
    await AsyncStorage.multiRemove(GUEST_CHAT_STORAGE_KEYS);
  } catch (error) {
    console.log("[guestChatStorage] Failed to clear guest chat storage", error);
  }
}
