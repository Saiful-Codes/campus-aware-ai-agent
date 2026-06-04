import { db } from "../lib/firebase";
import { collection, getDocs, deleteDoc } from "firebase/firestore";

export async function deleteUserChatHistory(userId: string) {
    if (!userId) return;
    const messagesRef = collection(db, "chats", userId, "messages");
    const snapshot = await getDocs(messagesRef);
    const deletions = snapshot.docs.map((doc) => deleteDoc(doc.ref));
    await Promise.all(deletions);
}
