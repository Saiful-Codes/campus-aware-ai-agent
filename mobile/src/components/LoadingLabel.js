import React, { useEffect, useRef } from "react";
import { Animated, Easing } from "react-native";

const MESSAGES = {
  live_sensor:    "Fetching from live sensor...",
  sensor_history: "Analyzing sensor data...",
  campus_docs:    "Reading and analyzing the database...",
  general:        "Thinking...",
};

export default function LoadingLabel({ sourceType }) {
  const opacity = useRef(new Animated.Value(0.4)).current;

  useEffect(() => {
    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, {
          toValue: 1.0,
          duration: 900,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(opacity, {
          toValue: 0.4,
          duration: 900,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    );
    animation.start();
    return () => animation.stop();
  }, []);

  const label = MESSAGES[sourceType] ?? MESSAGES.general;

  return (
    <Animated.Text style={{ opacity, color: "#888", fontSize: 13 }}>
      {label}
    </Animated.Text>
  );
}
