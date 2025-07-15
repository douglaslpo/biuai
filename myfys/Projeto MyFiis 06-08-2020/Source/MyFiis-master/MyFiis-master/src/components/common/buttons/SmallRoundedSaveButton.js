import React from "react";
import { StyleSheet, TouchableOpacity, Text, View } from "react-native";
import Spinner from "../Spinner";

const SmallRoundedSaveButton = (props) => {
  if (props.loading) {
    return (
      <View style={styles.spinner}>
        <Spinner size="small" />
      </View>
    );
  }

  return (
    <TouchableOpacity onPress={props.onPress} style={styles.touchableOpacity}>
      <Text style={styles.text}>{props.text}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  touchableOpacity: {
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "white",
    borderRadius: 100,
    alignSelf: "center",
    width: 150,
    height: 100,
    maxHeight: 30,
  },
  text: {
    alignSelf: "center",
    paddingLeft: 50,
    paddingRight: 50,
    paddingVertical: 10,
    color: "#26BFBD",
    fontSize: 14,
  },
  spinner: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
});

export default SmallRoundedSaveButton;
