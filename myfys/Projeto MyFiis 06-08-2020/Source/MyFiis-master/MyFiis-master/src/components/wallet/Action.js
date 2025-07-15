import React from "react";
import { StyleSheet, TouchableOpacity, Text } from "react-native";
import { normalize } from "../../lib/normalize";

const Action = (props) => {
  return (
    <TouchableOpacity onPress={props.onPress} style={styles.touchableOpacity}>
      <Text style={styles.text}>{props.text}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  touchableOpacity: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#1EBEA5",
    borderRadius: normalize(100),
    maxWidth: normalize(143),
    maxHeight: normalize(36),
    borderWidth: normalize(2),
    borderColor: "#00E1B5",
  },
  text: {
    paddingVertical: normalize(10),
    color: "#FFFFFF",
    fontSize: normalize(12),
    fontFamily: "Montserrat-SemiBold",
    fontStyle: "normal",
  },
});

export default Action;
