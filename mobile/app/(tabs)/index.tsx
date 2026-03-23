import { useEffect, useState } from "react";
import { View, Text, StyleSheet, ActivityIndicator } from "react-native";
import { fetchHealth } from "@/services/api";

export default function HomeScreen() {
  const [loading, setLoading] = useState(true);
  const [healthData, setHealthData] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadHealth = async () => {
      try {
        const data = await fetchHealth();
        setHealthData(data);
      } catch (err) {
        console.log("FETCH ERROR:", err);
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    loadHealth();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Campus-Aware AI Agent</Text>

      {loading && <ActivityIndicator size="large" />}

      {!loading && healthData && (
        <View style={styles.card}>
          <Text style={styles.success}>Backend connected</Text>
          <Text>Status: {healthData.status}</Text>
          <Text>Environment: {healthData.environment}</Text>
          <Text>Port: {healthData.port}</Text>
        </View>
      )}

      {!loading && error ? (
        <View style={styles.card}>
          <Text style={styles.error}>Connection failed</Text>
          <Text>{error}</Text>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: "700",
    marginBottom: 20,
  },
  card: {
    width: "100%",
    maxWidth: 320,
    padding: 16,
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 12,
    backgroundColor: "#f9f9f9",
    gap: 8,
  },
  success: {
    fontSize: 18,
    fontWeight: "700",
    color: "green",
  },
  error: {
    fontSize: 18,
    fontWeight: "700",
    color: "red",
  },
});