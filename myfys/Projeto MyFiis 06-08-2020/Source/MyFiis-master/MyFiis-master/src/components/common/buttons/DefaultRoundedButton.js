import React from "react";
import { StyleSheet, TouchableOpacity, Text } from "react-native";
import LinearGradient from "react-native-linear-gradient";
import { normalize } from "../../../lib/normalize";
const DefaultRoundedButton = (props) => {
  if (props.disabled) {
    return (
      <TouchableOpacity
        activeOpacity={1}
        onPress={() => {}}
        style={styles.touchableOpacityDisabled}
      >
        <LinearGradient
          useAngle={true}
          angle={166.36}
          locations={[0, 1]}
          start={{ x: 0.0, y: 0.0 }}
          end={{ x: 1, y: 1 }}
          colors={["#26BFBD", "#00E1B5"]}
          style={styles.linearDisabled}
        >
          <Text style={styles.text}>{props.text}</Text>
        </LinearGradient>
      </TouchableOpacity>
    );
  } else {
    return (
      <TouchableOpacity
        activeOpacity={0}
        onPress={() => {
          props.onPress();
        }}
        style={styles.touchableOpacity}
      >
        <LinearGradient
          useAngle={true}
          angle={166.36}
          locations={[0, 1]}
          start={{ x: 0.0, y: 0.0 }}
          end={{ x: 1, y: 1 }}
          colors={["#26BFBD", "#00E1B5"]}
          style={styles.linear}
        >
          <Text style={styles.text}>{props.text}</Text>
        </LinearGradient>
      </TouchableOpacity>
    );
  }
};

const styles = StyleSheet.create({
  touchableOpacity: {
    alignItems: "center",
    backgroundColor: "#1EBEA5",
    borderRadius: 100,
    marginTop: 20,
    alignSelf: "center",
    width: 200,
  },
  touchableOpacityDisabled: {
    alignItems: "center",
    backgroundColor: "#1ebea559",
    borderRadius: 100,
    marginTop: 20,
    alignSelf: "center",
    width: 200,
  },
  text: {
    alignSelf: "center",
    fontFamily: "Montserrat-Regular",
    paddingLeft: 50,
    paddingRight: 50,
    paddingTop: 15,
    paddingBottom: 15,
    color: "#FFFFFF",
    fontSize: normalize(12),
    opacity: 1,
    fontWeight: "bold",
  },
  linear: {
    borderRadius: 100,
    width: 200,
  },
  linearDisabled: {
    borderRadius: 100,
    width: 200,
    opacity: 0.5,
  },
});

export default DefaultRoundedButton;
