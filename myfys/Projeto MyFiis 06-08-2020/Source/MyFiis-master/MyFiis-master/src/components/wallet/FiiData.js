import React, { Component } from "react";
import { View, StyleSheet, Text } from "react-native";
import { normalize } from "../../lib/normalize";

export default class FiiData extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    return (
      <View style={styles.container}>
        <View style={styles.column}>
          <View style={styles.row}>
            <Text style={styles.rowTitle} opacity={0.5}>
              Nome
            </Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.rowDescription}>
              {this.props.fii.name ? this.props.fii.name : this.props.fii.code}
            </Text>
          </View>
        </View>

        <View style={styles.column}>
          <View style={styles.row}>
            <Text style={styles.rowTitle} opacity={0.5}>
              Segmento
            </Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.rowDescription}>
              {this.props.fii.segment
                ? this.props.fii.segment
                : this.props.fii.code}
            </Text>
          </View>
        </View>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
    backgroundColor: "#FFFF",
    marginVertical: 10,
    marginHorizontal: 14,
    borderRadius: 10,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.23,
    shadowRadius: 2.62,
    elevation: 4,
    maxHeight: 70,
    height: 70,
  },

  column: {
    flex: 1,
    borderRadius: 10,
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
  },

  row: {
    flex: 1,
    alignItems: "center",
    justifyContent: "space-around",
  },

  rowTitle: {
    color: "#222222",
    fontSize: normalize(12),
    marginBottom: -10,
    fontFamily: "Montserrat-Semibold",
    opacity: 0.5,
    lineHeight: normalize(15),
  },

  rowDescription: {
    fontWeight: "500",
    color: "#0567D0",
    lineHeight: normalize(15),
    fontSize: normalize(12),
    marginTop: -10,
    fontFamily: "Montserrat-Regular",
    paddingHorizontal: 5,
    textAlign: "center",
  },
});
