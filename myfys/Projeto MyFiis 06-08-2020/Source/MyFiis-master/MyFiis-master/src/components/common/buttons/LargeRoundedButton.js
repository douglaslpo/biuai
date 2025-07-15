import React from "react";
import { StyleSheet, TouchableOpacity, Text, Dimensions } from "react-native";
import LinearGradient from "react-native-linear-gradient";
import { normalize } from "../../../lib/normalize";

const windowHeight = Dimensions.get("window").height;

const LargeRoundedButton = (props) => {
  const disabled = props.disabled;

  return (
    <TouchableOpacity
      activeOpacity={1}
      onPress={
        disabled
          ? () => {}
          : () => {
              props.onPress();
            }
      }
      style={styles.touchableOpacity}
    >
      <LinearGradient
        useAngle={true}
        angle={166.36}
        locations={[0, 1]}
        start={{ x: 0.0, y: 0.0 }}
        end={{ x: 1, y: 1 }}
        colors={["#26BFBD", "#00E1B5"]}
        style={
          disabled
            ? { ...styles.linearGradient, opacity: 0.5 }
            : styles.linearGradient
        }
      >
        <Text style={styles.text}>{props.text}</Text>
      </LinearGradient>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  touchableOpacity: {
    width: "100%",
    marginTop: "10%",
    borderRadius: 100,
  },

  text: {
    fontFamily: "Montserrat-Bold",
    paddingVertical: windowHeight / 40,
    color: "#FFFFFF",
    fontSize: normalize(16),

  },

  linearGradient: {
    flex:1,
    borderRadius: 100,
    width: "100%",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
  },
});

export default LargeRoundedButton;
