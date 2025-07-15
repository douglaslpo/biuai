import React, { Component } from "react";
import { View, Text, StyleSheet } from "react-native";
import { TouchableOpacity } from "react-native-gesture-handler";
import Icon from "react-native-vector-icons/Ionicons";
import Spinner from "../Spinner";

export default class ForwardButton extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    const isLoading = this.props.isLoading;
    let enabled = this.props.enabled;
    
    if (isLoading)
      return (
        <View style={styles.button}>
          <Spinner size="small" />
        </View>
      );

    if (enabled) {
      return (
        <TouchableOpacity style={styles.button} onPress={this.props.onPress}>
          <Icon style={styles.icon} name="ios-arrow-round-forward" size={40} />
        </TouchableOpacity>
      );
    } else {
      return (
        <TouchableOpacity style={styles.buttonDisabled}>
          <Icon style={styles.icon} name="ios-arrow-round-forward" size={40} />
        </TouchableOpacity>
      );
    }
  }
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: "#1EBEA5",
    width: 50,
    height: 50,
    borderRadius: 1000,
    alignItems: "center",
    justifyContent: "center",
  },

  buttonDisabled: {
    backgroundColor: "rgba(30, 190, 165, 0.5)",
    width: 50,
    height: 50,
    borderRadius: 1000,
    alignItems: "center",
    justifyContent: "center",
  },

  icon: {
    color: "#FFFF",
    alignSelf: "center",
  },
});
