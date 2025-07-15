import React, { Component } from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import Icon from "react-native-vector-icons/Ionicons";
import { normalize } from "../../lib/normalize";
class Header extends Component {
  render() {
    return (
      <View style={[styles.container, this.props.style]}>
        <View style={styles.titleContainer}>
          <Text style={styles.title}>{this.props.title}</Text>
        </View>

        <TouchableOpacity
          style={styles.backButton}
          onPress={() => this.props.onPress()}
        >
          <Icon name="ios-arrow-round-back" style={styles.iconButton} />
        </TouchableOpacity>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    height: normalize(60),
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "flex-start",
    backgroundColor: "#1EBEA5",
  },

  titleContainer: {
    flexGrow: 1,
    flexDirection: "row",
    justifyContent: "center",
  },

  title: {
    color: "#FFFF",
    fontSize: normalize(14),
  },

  backButton: {
    marginLeft: 10,
    position: "absolute",
  },

  iconButton: {
    fontSize: normalize(30),
    color: "#FFFF",
  },
});

export default Header;
