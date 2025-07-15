import React, { Component } from "react";
import { View, Text, StyleSheet } from "react-native";
import { normalize } from "../../lib/normalize";
export default class Total extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    return (
      <View style={styles.container}>
        <Text
          style={{
            ...styles.total,
            ...(this.props.customStyle
              ? this.props.customStyle
              : { color: "#0567D0" }),
          }}
        >
          {this.props.text}
        </Text>
        <Text style={styles.totalDescription}>{this.props.caption}</Text>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    alignSelf: "center",
  },

  total: {
    fontSize: normalize(25),
    alignSelf: "center",
  },

  totalDescription: {
    color: "#343F53",
    fontSize: normalize(12),
    fontWeight: "600",
    alignSelf: "center",
  },
});
