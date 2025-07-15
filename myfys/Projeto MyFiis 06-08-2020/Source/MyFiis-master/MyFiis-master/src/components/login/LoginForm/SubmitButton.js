import React from "react";
import { TouchableOpacity, Text, View, StyleSheet, Image } from "react-native";
import Spinner from "../LoginForm/Spinner";
import ArrowButton from "../../common/svgs/ArrowButton";

const SubmitButton = (props) => {
  const isLoading = props.isLoading;

  if (isLoading) {
    return (
      <View style={styles.touchable}>
        <Spinner size="small" />
      </View>
    );
  }
  return (
    <TouchableOpacity style={styles.touchable} onPress={props.onPress}>
      <ArrowButton />
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  touchable: {
    padding: 10,
    color: "rgba(58, 176, 162, 0.5)",
    fontWeight: "bold",
    alignSelf: "flex-end",
    marginRight: 25,
    marginBottom: 15,
    paddingTop: 25,
    fontSize: 15,
  },
});

export default SubmitButton;
