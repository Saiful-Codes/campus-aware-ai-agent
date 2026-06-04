import {
    addDoc,
    collection,
    deleteDoc,
    doc,
    getDocs,
    increment,
    onSnapshot,
    orderBy,
    query,
    serverTimestamp,
    updateDoc,
} from "firebase/firestore";
import { db } from "./firebase";

export type FirestoreChatThread = {
    id: string;
    title: string;
    lastMessage: string;
    messageCount: number;
    updatedAtMs: number;
    createdAtMs: number;
};

export type FirestoreChatMessage = {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestampMs: number;
    intent?: string;
    usedDatabase?: boolean;
    usedGemini?: boolean;
};

function toMillis(value: unknown): number {
    if (value && typeof value === "object" && "toMillis" in (value as Record<string, unknown>)) {
        try {
            return (value as { toMillis: () => number }).toMillis();
        } catch {
            return Date.now();
        }
    }
    return Date.now();
}

export function chatsCollectionRef(userId: string) {
    return collection(db, "users", userId, "chats");
}

export function messagesCollectionRef(userId: string, chatId: string) {
    return collection(db, "users", userId, "chats", chatId, "messages");
}

export async function createChatThread(userId: string): Promise<string> {
    const ref = await addDoc(chatsCollectionRef(userId), {
        title: "New Chat",
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp(),
        lastMessage: "",
        messageCount: 0,
    });
    return ref.id;
}

export function subscribeChatThreads(
    userId: string,
    onData: (threads: FirestoreChatThread[]) => void,
    onError?: (error: Error) => void
) {
    const q = query(chatsCollectionRef(userId), orderBy("updatedAt", "desc"));

    return onSnapshot(
        q,
        (snapshot) => {
            const rows: FirestoreChatThread[] = snapshot.docs.map((d) => {
                const data = d.data() as Record<string, unknown>;
                return {
                    id: d.id,
                    title: String(data.title ?? "New Chat"),
                    lastMessage: String(data.lastMessage ?? ""),
                    messageCount: Number(data.messageCount ?? 0),
                    updatedAtMs: toMillis(data.updatedAt),
                    createdAtMs: toMillis(data.createdAt),
                };
            });

            onData(rows);
        },
        (error) => {
            if (onError) onError(error);
        }
    );
}

export function subscribeChatMessages(
    userId: string,
    chatId: string,
    onData: (messages: FirestoreChatMessage[]) => void,
    onError?: (error: Error) => void
) {
    const q = query(messagesCollectionRef(userId, chatId), orderBy("timestamp", "asc"));

    return onSnapshot(
        q,
        (snapshot) => {
            const rows: FirestoreChatMessage[] = snapshot.docs.map((d) => {
                const data = d.data() as Record<string, unknown>;
                return {
                    id: d.id,
                    role: (data.role as "user" | "assistant") ?? "assistant",
                    content: String(data.content ?? ""),
                    timestampMs: toMillis(data.timestamp),
                    intent: data.intent ? String(data.intent) : undefined,
                    usedDatabase:
                        typeof data.usedDatabase === "boolean" ? data.usedDatabase : undefined,
                    usedGemini: typeof data.usedGemini === "boolean" ? data.usedGemini : undefined,
                };
            });

            onData(rows);
        },
        (error) => {
            if (onError) onError(error);
        }
    );
}

export async function appendChatMessage(
    userId: string,
    chatId: string,
    message: {
        role: "user" | "assistant";
        content: string;
        intent?: string;
        usedDatabase?: boolean;
        usedGemini?: boolean;
    }
) {
    await addDoc(messagesCollectionRef(userId, chatId), {
        role: message.role,
        content: message.content,
        timestamp: serverTimestamp(),
        ...(message.intent ? { intent: message.intent } : {}),
        ...(typeof message.usedDatabase === "boolean"
            ? { usedDatabase: message.usedDatabase }
            : {}),
        ...(typeof message.usedGemini === "boolean"
            ? { usedGemini: message.usedGemini }
            : {}),
    });
}

export async function updateChatMetadata(
    userId: string,
    chatId: string,
    updates: {
        title?: string;
        lastMessage?: string;
        messageIncrement?: number;
    }
) {
    const payload: Record<string, unknown> = {
        updatedAt: serverTimestamp(),
    };

    if (updates.title) payload.title = updates.title;
    if (typeof updates.lastMessage === "string") payload.lastMessage = updates.lastMessage;
    if (updates.messageIncrement) payload.messageCount = increment(updates.messageIncrement);

    await updateDoc(doc(db, "users", userId, "chats", chatId), payload);
}

export async function deleteChatThread(userId: string, chatId: string) {
    const messagesSnap = await getDocs(messagesCollectionRef(userId, chatId));

    await Promise.all(messagesSnap.docs.map((m) => deleteDoc(m.ref)));
    await deleteDoc(doc(db, "users", userId, "chats", chatId));
}

export async function clearAllChatThreads(userId: string) {
    const chatsSnap = await getDocs(chatsCollectionRef(userId));
    for (const c of chatsSnap.docs) {
        await deleteChatThread(userId, c.id);
    }
}
