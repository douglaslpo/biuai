import React from "react";
import { StyleSheet, TouchableOpacity, Text, View } from "react-native";
import Spinner from "../Spinner";

const SmallRoundedButton = (props) => {
  if (props.loading) {
    return (
      <View style={styles.spinner}>
        <Spinner size="small" />
      </View>
    );
  }

  if (props.canSubmit === true) {
    return (
      <TouchableOpacity onPress={props.onPress} style={styles.touchableOpacity}>
        <Text style={styles.text}>{props.text}</Text>
      </TouchableOpacity>
    );
  } else {
    return (
      <TouchableOpacity style={styles.touchableOpacityDisabled}>
        <Text style={styles.text}>{props.text}</Text>
      </TouchableOpacity>
    );
  }
};

const styles = StyleSheet.create({
  touchableOpacity: {
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#1EBEA5",
    borderRadius: 100,
    alignSelf: "center",
    width: 150,
    maxHeight: 30,
  },
  touchableOpacityDisabled: {
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(30, 190, 165, 0.5)",
    borderRadius: 100,
    alignSelf: "center",
    width: 150,
    maxHeight: 30,
  },
  text: {
    alignSelf: "center",
    paddingLeft: 50,
    paddingRight: 50,
    paddingVertical: 10,
    color: "#FFFFFF",
    fontSize: 12,
    fontStyle: "normal",
    lineHeight: 15,
    fontFamily: "Montserrat-SemiBold",
  },
  spinner: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
});

export default SmallRoundedButton;
